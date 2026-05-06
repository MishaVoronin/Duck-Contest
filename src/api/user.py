from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from services.user_service import (
    register_user,
    login_user,
    logout_user,
    get_current_user,
)
from database.core.db import get_db


router = APIRouter(prefix="/user", tags=["работа с пользователями"])
templates = Jinja2Templates(directory="templates")


@router.get(
    "/", summary="Получить список всех пользователей", response_class=HTMLResponse
)
async def all():
    return RedirectResponse(url="login")  # заглушка


@router.get("/login", summary="авторизация", name="login", response_class=HTMLResponse)
async def login(req: Request):
    return templates.TemplateResponse(request=req, name="user/login.html")


@router.post("/login")
async def _login(
    response: Response,
    login: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await login_user(db, login, password)


@router.get(
    "/register", summary="авторизация", name="register", response_class=HTMLResponse
)
async def register(req: Request):
    return templates.TemplateResponse(request=req, name="user/register.html")


@router.post("/register")
async def _register(
    name: Annotated[str, Form()],
    login: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: AsyncSession = Depends(get_db),
):
    return await register_user(db, name, login, password)


@router.get("/logout", name="logout")
async def logout():
    return await logout_user()


@router.get("/test", name="test")
async def test(request: Request, user=Depends(get_current_user)):
    if user is None:
        res = f"u are not authorized.<br><a href='{request.url_for('login')}'>login</a> or <a href='{request.url_for('register')}'>register</a>"
    else:
        res = f"hello, {user.name}<br><a href='{request.url_for('logout')}'>logout</a>"
    return HTMLResponse(res)
