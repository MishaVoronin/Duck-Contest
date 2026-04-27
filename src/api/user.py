from fastapi import APIRouter, Request, Form, Depends,HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from services.user_service import UserResponse, TokenResponse, RefreshTokenRequest, register_user
from crud.user import get_user_by_id, get_user_by_login
from crud.refresh_token import create_refresh_token
from database.core.db import get_db
import uuid
import scripts.auth as auth
router = APIRouter(prefix='/user', tags=['работа с пользователями'])
templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme),db: AsyncSession = Depends(get_db)) -> User:
    """Получение текущего пользователя из токена"""
    user_id = auth.get_user_id_from_token(token)
    payload = auth.decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    return get_user_by_id(db,user_id)

def require_status(allowed_statuses: List[UserStatusEnum]):
    """Декоратор для проверки статуса пользователя"""
    async def dependency(current_user: User|None = Depends(get_current_user)):
        if current_user is None or current_user.status not in allowed_statuses:
            raise HTTPException(status_code=403,detail=f"Access denied. Required status: {[s.value for s in allowed_statuses]}")
        return current_user
    return dependency




@router.get('/', summary="Получить список всех пользователей", response_class=HTMLResponse)
async def all():
    return RedirectResponse(url='login')#заглушка
@router.get('/login', summary="авторизация", response_class=HTMLResponse)
async def login(req: Request):
    return templates.TemplateResponse(request=req, name='user/login.html')

@router.post('/login', response_model=TokenResponse)
async def _login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None, db: AsyncSession = Depends(get_db)):
    print(dir(form_data))
    print(form_data.username)
    print(form_data.password)
    user=await get_user_by_login(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid login or password")
    ccess_token = auth.create_access_token(user.id)
    refresh_token = auth.create_refresh_token(user.id)
    create_refresh_token(db, RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS),

    ))
    #return RedirectResponse(url='login', status_code=status.HTTP_303_SEE_OTHER)
    return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

@router.get('/register', summary="авторизация", response_class=HTMLResponse)
async def register(req:Request):
    return templates.TemplateResponse(request=req, name='user/register.html')

@router.post('/register',response_model=UserResponse)
async def _register(name: Annotated[str, Form()], login: Annotated[str, Form()], password: Annotated[str, Form()], db: AsyncSession = Depends(get_db)):
    if await get_user_by_login(db, login):
        raise HTTPException(status_code=400, detail="Login already taken")
    user = await register_user(db, name,login,password)
    return user
    #return RedirectResponse(url='register', status_code=status.HTTP_303_SEE_OTHER)


@router.get('/profile/{uuid:uuid.UUID}', summary="профиль пользователя", response_class=HTMLResponse)
async def profile(req, id: uuid.UUID):
    #user =
    return templates.TemplateResponse(request=req, name='user/profile.html', context={"user":"user"})
