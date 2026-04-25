from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uuid
import bcrypt
router = APIRouter(prefix='/user', tags=['работа с пользователями'])
templates = Jinja2Templates(directory="templates")

def crypt(string: str)->str:
    return bcrypt.hashpw(string.encode("utf-8"), bcrypt.gensalt())

@router.get('/', summary="Получить список всех пользователей", response_class=HTMLResponse)
async def all():
    return RedirectResponse(url="/login")#заглушка
@router.get('/login', summary="авторизация", response_class=HTMLResponse)
async def login(req):
    return templates.TemplateResponse(request=req, name='user/login.html')
@router.post('/login')
async def login(login, password):
    return {"login":login, "password":crypt(password)}
@router.get('/register', summary="авторизация", response_class=HTMLResponse)
async def register(req):
    return templates.TemplateResponse(request=req, name='user/register.html')
@router.get('/profile/{uuid:uuid.UUID}', summary="профиль пользователя", response_class=HTMLResponse)
async def profile(req, id: uuid.UUID):
    #user =
    return templates.TemplateResponse(request=req, name='user/profile.html', context={"user":"user"})
