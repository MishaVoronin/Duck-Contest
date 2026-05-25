from fastapi import Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from jose import JWTError

from crud import user_crud, refresh_token_crud
from database.models.base import User, RefreshToken, UserStatusEnum
from core import auth
from core.db import get_db
from schemas import user_schemas

COOKIE_SECURE = False
COOKIE_SAMESITE = "lax"


async def get_user_info(
    db: AsyncSession, user: User, name: str
) -> user_schemas.UserInfoResponse:
    user_info: User | None = user_crud.get_user_by_name(db, name)
    if user_info is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user_schemas.UserInfoResponse(
        user_info=user_schemas.UserInfo(
            name=user_info.name,
            SFP=user_info.sfp,
            status=user_info.status,
        ),
        is_moderator=False
        if user_info is None
        else user.status == UserStatusEnum.MODERATOR,
        is_me=False if user_info is None else user.id == user_info.id,
    )


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
    user = await user_crud.get_user_by_id(db, login)
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
    db: AsyncSession, data: user_schemas.RegisterUserInput
) -> User | None:
    if await user_crud.get_user_by_login(db, data.login):
        return JSONResponse(content={"message": "user already exists"})
    user: User = User(
        name=data.name,
        login=data.login,
        hash_password=auth.hash_password(data.password),
    )
    await user_crud.create_user(db, user)

    return await login_user(
        db, user_schemas.LoginInput(login=user.login, password=data.password)
    )


async def login_user(db: AsyncSession, data: user_schemas.LoginInput) -> dict:
    user = await user_crud.get_user_by_login(db, data.login)
    if not user or not auth.verify_password(data.password, user.hash_password):
        raise HTTPException(status_code=401, detail="Invalid login or password")
    refresh = auth.create_refresh_token(user.id)
    access = auth.create_access_token(user.id)
    await refresh_token_crud.save_refresh_token(
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
    rt = await refresh_token_crud.get_refresh_token_by_jwt(db, token)
    if not rt:
        raise HTTPException(status_code=401, detail="Token not found in DB")
    await refresh_token_crud.revoke_token(db, rt)

    user_id = payload["sub"]
    access = auth.create_access_token(user_id)
    refresh = auth.create_refresh_token(user_id)
    await refresh_token_crud.save_refresh_token(
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
        return JSONResponse(content={"message": "Refresh token missing"})
    payload = auth.decode_token(token, "refresh")
    rt = await refresh_token_crud.get_refresh_token_by_jwt(db, token)
    if not rt or rt.is_revoked:
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
    user = await user_crud.get_user_by_id(db, payload["sub"])
    return JSONResponse(
        content={
            "name": user.name, 
            "login": user.login
        }, headers=response.headers
    )


async def logout_user(request: Request, db: AsyncSession):
    token = request.cookies.get("refresh_token")
    if token is not None:
        rt = await refresh_token_crud.get_refresh_token_by_jwt(db, token)
        if rt is not None and not rt.is_revoked:
            await refresh_token_crud.revoke_token(db, rt)
    response = RedirectResponse("test")
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return response
