from fastapi import APIRouter, Request, Form, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from database.models.base import User
from services.user_service import (
    register_user,
    login_user,
    logout_user,
    get_current_user,
    is_loggined,
    refresh,
    restore_session,
)
from core.db import get_db


router = APIRouter(prefix="/user", tags=["работа с пользователями"])
templates = Jinja2Templates(directory="templates")
LOGIN_REDIRECT = "test"


@router.get(
    "/", summary="Получить список всех пользователей", response_class=HTMLResponse
)
async def all(f=Depends(is_loggined)):
    return (
        RedirectResponse(url="test") if f else RedirectResponse(url="login")
    )  # заглушка


@router.get("/login", summary="авторизация", name="login", response_class=HTMLResponse)
async def login(req: Request, f: bool = Depends(is_loggined)):
    if f:
        return RedirectResponse(url=LOGIN_REDIRECT)
    return templates.TemplateResponse(
        request=req, name="user/login.html", context={"redirect": LOGIN_REDIRECT}
    )


@router.post("/login")
async def _login(
    response: Response,
    login: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await login_user(db, login, password)


@router.post("/refresh")
async def refresh_route(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    return await refresh(request, response, db)


@router.post("/restore")
async def restore(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    return await restore_session(request, response, db)


@router.get(
    "/register", summary="авторизация", name="register", response_class=HTMLResponse
)
async def register(req: Request, f: bool = Depends(is_loggined)):
    if f:
        return RedirectResponse(url=LOGIN_REDIRECT)
    return templates.TemplateResponse(
        request=req, name="user/register.html", context={"redirect": LOGIN_REDIRECT}
    )


@router.post("/register")
async def _register(
    name: Annotated[str, Form()],
    login: Annotated[str, Form()],
    password: Annotated[str, Form()],
    db: AsyncSession = Depends(get_db),
):
    return await register_user(db, name, login, password)


@router.get("/logout", name="logout")
async def logout(request: Request, db: AsyncSession = Depends(get_db)):
    return await logout_user(request, db)


@router.get("/test", name="test")
async def test(request: Request):
    return templates.TemplateResponse(request=request, name="user/profile.html")


@router.post("/me", name="me")
async def me(user: User = Depends(get_current_user)):
    return None if user is None else {"name": user.name, "login": user.login}
