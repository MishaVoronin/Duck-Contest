
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Result, select
import uuid
from database.models.base import RefreshToken
from typing import Tuple


async def create_refresh_token(db: AsyncSession, token: RefreshToken) -> RefreshToken:
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token
