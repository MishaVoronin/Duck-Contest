from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from database.models.base import ContestAccess


async def add_access(db: AsyncSession, contestaccess: ContestAccess):
    db.add(contestaccess)
    await db.commit()
    await db.refresh(contestaccess)
    return contestaccess


async def get_access_by_user_and_contest(
    db: AsyncSession, user_id: uuid.UUID, contest_id: uuid.UUID
):
    result = await db.execute(
        select(ContestAccess).where(
            ContestAccess.user_id == user_id, ContestAccess.contest_id == contest_id
        )
    )
    return result.scalar_one_or_none()
