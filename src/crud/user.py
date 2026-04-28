from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from database.models.base import User


async def create_user(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, uuid: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == uuid))
    return result.scalar_one_or_none()


async def get_user_by_login(db: AsyncSession, login: str) -> User | None:
    result = await db.execute(select(User).where(User.login == login))
    return result.scalar_one_or_none()
