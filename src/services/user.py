from crud import user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.base import User
import bcrypt
from jose import jwt, JWTError
import os
SECRET_KEY = os.getenv("SECRET_KEY", "very_hard_secret_key")


async def register(db: AsyncSession,name: str, login: str, password: str) -> str|None:
    if not user.get_by_login(login):
        user.create_user(User(name=name,login=login, password=password))
        return jwt({"login":login,"password":password}, SECRET_KEY, algorithm="HS256").encode()
    return None

async def login(db: AsyncSession, login: str, password: str) -> str|None:
    u = user.get_by_login(login)
    if u and u.password==password:
        return jwt({"login":login,"password":password}, SECRET_KEY, algorithm="HS256").encode()
    return None
