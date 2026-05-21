from fastapi import Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud.user_crud import get_user_by_id, get_user_by_login, create_user
from crud.refresh_token_crud import (
    save_refresh_token,
    get_refresh_token_by_jwt,
    revoke_token,
)
from database.models.base import User, RefreshToken
import scripts.auth as auth
from datetime import datetime, timedelta
from database.core.db import get_db
from jose import JWTError

COOKIE_SECURE = False
COOKIE_SAMESITE = "lax"


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User | None:
    token = request.cookies.get("access_token")
    if token is None:
        refresh = request.cookies.get("refresh_token")
        if refresh is None:
            return None
        return None
    try:
        payload = auth.decode_token(token, "access")
        login = payload.get("sub")
        if login is None:
            return None
    except JWTError:
        return None
    except AttributeError:
        return None
    user = await get_user_by_id(db, login)
    if user is None:
        return None
    return user


async def require_user(
    status: dict | str | None = None, user: User | None = Depends(get_current_user)
) -> User:
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


async def is_loggined(user: User | None = Depends(get_current_user)) -> bool:
    return user is not None


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
        User(name=name, login=login, password=auth.hash_password(password)),
    )
    return await login_user(db, login, password)


async def login_user(db: AsyncSession, login: str, password: str) -> dict:
    user = await get_user_by_login(db, login)
    if not user or not auth.verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid login or password")
    refresh = auth.create_refresh_token(user.id)
    access = auth.create_access_token(user.id)
    await save_refresh_token(
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


async def refresh(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    payload = auth.decode_token(token, "refresh")
    rt = await get_refresh_token_by_jwt(db, token)
    if not rt:
        raise HTTPException(status_code=401, detail="Token not found in DB")
    await revoke_token(db, rt)

    user_id = payload["sub"]
    access = auth.create_access_token(user_id)
    refresh = auth.create_refresh_token(user_id)
    await save_refresh_token(
        db,
        RefreshToken(
            user_id=user_id,
            token=refresh,
            expires_at=datetime.utcnow()
            + timedelta(days=auth.REFRESH_TOKEN_EXPIRE_DAYS),
        ),
    )

    set_auth_cookies(response, access, refresh)
    return {"message": "Tokens rotated"}


async def restore_session(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
):
    token = request.cookies.get("refresh_token")
    if not token:
        # raise HTTPException(status_code=401, detail="Refresh token missing")
        return JSONResponse(content={"message": "Refresh token missing"})
    payload = auth.decode_token(token, "refresh")
    rt = await get_refresh_token_by_jwt(db, token)
    if not rt or rt.is_revoked:
        # raise HTTPException(status_code=401, detail="Session revoked")
        return JSONResponse(content={"message": "Session revoked"})
    access_token = auth.create_access_token(payload["sub"])
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    user = await get_user_by_id(db, payload["sub"])
    # print(payload["sub"],'ok')
    return JSONResponse(
        content={"name": user.name, "login": user.login}, headers=response.headers
    )


async def logout_user(request: Request, db: AsyncSession):
    token = request.cookies.get("refresh_token")
    if token:
        rt = await get_refresh_token_by_jwt(db, token)
        if rt and not rt.is_revoked:
            await revoke_token(db, rt)
    response = RedirectResponse("test")
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return response
