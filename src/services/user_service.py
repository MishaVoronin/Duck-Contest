from fastapi import Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud.user import get_user_by_id, get_user_by_login, create_user
from crud.refresh_token import create_refresh_token
from database.models.base import User, RefreshToken
import scripts.auth as auth
from datetime import datetime, timedelta
from database.core.db import get_db
from jose import JWTError

COOKIE_SECURE = True
COOKIE_SAMESITE = "strict"


async def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token")
    # if not token:
    #    raise HTTPException(status_code=401, detail="Not authenticated")
    return token


async def get_current_user(
    token: str = Depends(get_token_from_cookie), db: AsyncSession = Depends(get_db)
) -> User:
    if token is None:
        return None
    credentials_exception = HTTPException(status_code=401, detail="Invalid credentials")
    try:
        payload = auth.decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        login = payload.get("sub")
        if login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_id(db, login)
    if user is None:
        raise credentials_exception
    return user


async def require_user(status: dict | str | None = None):
    user = await get_current_user()
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if status is not None and (
        isinstance(status, dict)
        and user.status not in status
        or isinstance(status, str)
        and user.status != status
    ):
        raise HTTPException(status_code=401, detail="Not enough rights")
    return user


def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=int(
            timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()
        ),
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=int(timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
        path="/",
    )


async def register_user(
    db: AsyncSession, name: str, login: str, password: str
) -> User | None:
    if await get_user_by_login(db, login):
        return JSONResponse(content={"message": "user already exists"})
    await create_user(
        db,
        User(name=name, login=login, password=await auth.hash_password(password)),
    )
    return await login_user(db, login, password)


async def login_user(db: AsyncSession, login: str, password: str) -> dict:
    user = await get_user_by_login(db, login)
    if not user or not await auth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid login or password")
    refresh = auth.create_refresh_token(user.id)
    access = auth.create_access_token(user.id)
    await create_refresh_token(
        db,
        RefreshToken(
            user_id=user.id,
            token=refresh,
            expires_at=datetime.utcnow()
            + timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS),
        ),
    )
    response = JSONResponse(content={"message": "login"})
    set_auth_cookies(response, access, refresh)
    return response


async def logout_user():
    response = RedirectResponse("test")
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return response
