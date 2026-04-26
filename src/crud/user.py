from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.base import User


async def get_user_by_login(db: AsyncSession, login: str) -> User | None:
    result = await db.execute(select(User).where(User.login == login))
    return result.scalar_one_or_none()

async def add_user_to_db(db: AssertionError, new_user:User):
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user