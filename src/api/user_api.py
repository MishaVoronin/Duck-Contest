from fastapi import APIRouter, Request, Depends, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.base import User
from schemas import user_schemas
from services import user_service
from core.db import get_db

router = APIRouter(prefix="/user", tags=["работа с пользователями"])
templates = Jinja2Templates(directory="templates")
LOGIN_REDIRECT = "test"


@router.get("/n_{name}/get", response_model=user_schemas.UserInfoResponse)
async def get_user_info(
    name: str,
    user: User = Depends(user_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.get_user_info(db, user, name)


@router.post("/register")
async def register(
    data: user_schemas.RegisterUserInput,
    db: AsyncSession = Depends(get_db),
):
    return await user_service.register_user(db, data)


@router.post("/login")
async def login(
    data: user_schemas.LoginInput,
    db: AsyncSession = Depends(get_db),
):
    return await user_service.login_user(db, data)


@router.post("/logout")
async def logout(request: Request, db: AsyncSession = Depends(get_db)):
    return await user_service.logout_user(request, db)


@router.post("/refresh")
async def refresh_route(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    return await user_service.refresh(request, response, db)


@router.post("/restore")
async def restore(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    return await user_service.restore_session(request, response, db)
