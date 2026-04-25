
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from database.models.base import User


async def create_user(db: AsyncSession, user: User):
    db.add(user)

async def get_user_by_id(db: AsyncSession, uuid: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.uuid == uuid))
    # TODO
async def get_user_by_login(db: AsyncSession, login: str) -> User | None:
    return await db.execute(User).where(login=login).first()
