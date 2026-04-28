from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud.user import get_user_by_id, get_user_by_login, create_user
from crud.refresh_token import create_refresh_token
from database.models.base import User, RefreshToken, UserStatusEnum
import scripts.auth as auth
from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login", auto_error=False)


async def get_current_user(db, token: str = Depends(oauth2_scheme)) -> User:
    """Получение текущего пользователя из токена"""
    if not isinstance(token,str):
        return None
    user_id = await auth.get_user_id_from_token(token)
    payload = await auth.decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    return await get_user_by_id(db, user_id)


def require_status(allowed_statuses: list[UserStatusEnum]):
    """Декоратор для проверки статуса пользователя"""

    async def dependency(current_user: User | None = Depends(get_current_user)):
        if current_user is None or current_user.status not in allowed_statuses:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required status: {[s.value for s in allowed_statuses]}",
            )
        return current_user

    return dependency


async def register_user(
    db: AsyncSession, name: str, login: str, password: str
) -> User | None:
    if not await get_user_by_login(db, login):
        return await create_user(
            db,
            User(name=name, login=login, password=await auth.hash_password(password)),
        )
    return None


async def login_user(
    db: AsyncSession, login: str, password: str
) -> RedirectResponse | HTMLResponse:
    user = await get_user_by_login(db, login)
    if not user or not await auth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid login or password")
    result = RedirectResponse(url="login", status_code=status.HTTP_303_SEE_OTHER)
    refresh = await auth.create_refresh_token(user.id)
    await create_refresh_token(
        db,
        RefreshToken(
            user_id=user.id,
            token=refresh,
            expires_at=datetime.utcnow()
            + timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS),
        ),
    )
    result.set_cookie(
        key="access",
        value=await auth.create_access_token(user.id),
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=True,
        httponly=True,
        samesite="lax",
    )
    result.set_cookie(
        key="refresh",
        value=refresh,
        max_age=timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS),
        secure=True,
        httponly=True,
        samesite="lax",
    )

    return result
