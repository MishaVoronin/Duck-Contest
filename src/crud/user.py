
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from database.models.base import User


async def get_user_by_id(db: AsyncSession, id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == id))
    # TODO
