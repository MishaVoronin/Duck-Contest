from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from services.user_service import register_user, login_user
from database.core.db import get_db
from services.user_service import get_current_user
import uuid

router = APIRouter(prefix="/user", tags=["работа с пользователями"])
templates = Jinja2Templates(directory="templates")


@router.get(
    "/", summary="Получить список всех пользователей", response_class=HTMLResponse
)
async def all():
    return RedirectResponse(url="login")  # заглушка


@router.get("/login", summary="авторизация", response_class=HTMLResponse)
async def login(req: Request):
    return templates.TemplateResponse(request=req, name="user/login.html")


@router.post("/login")
async def _login(
    login: Annotated[str, Form()],
    password: Annotated[str, Form()],
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    #print(await get_current_user(db, request.cookies["access"]))
    await get_current_user(db)
    return await login_user(db, login, password)


@router.get("/register", summary="авторизация", response_class=HTMLResponse)
async def register(req: Request):
    return templates.TemplateResponse(request=req, name="user/register.html")


@router.post("/register")
async def _register(
    name: Annotated[str, Form()],
    login: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: AsyncSession = Depends(get_db),
):
    await register_user(db, name, login, password)
    return RedirectResponse(url="register", status_code=status.HTTP_303_SEE_OTHER)


@router.get(
    "/profile/{uuid:uuid.UUID}",
    summary="профиль пользователя",
    response_class=HTMLResponse,
)
async def profile(req, id: uuid.UUID):
    return templates.TemplateResponse(
        request=req, name="user/profile.html", context={"user": "user"}
    )
