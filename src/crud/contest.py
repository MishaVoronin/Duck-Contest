from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.base import Contest


async def add_contest(db: AsyncSession, contest: Contest) -> Contest:
    db.add(contest)
    await db.commit()
    await db.refresh(contest)
    return contest


async def get_contest_by_slug(db: AsyncSession, slug: str) -> Contest | None:
    result = await db.execute(select(Contest).where(Contest.slug == slug))
    return result.scalar_one_or_none()


async def delete_contest_from_db(db: AsyncSession, contest: Contest) -> None:
    await db.delete(Contest)
    await db.commit()


async def update_contest(
    db: AsyncSession, contest: Contest, name: str, is_active: bool, is_public: bool
) -> Contest:
    contest.name = name
    contest.is_active = is_active
    contest.is_public = is_public
    await db.commit()
    await db.refresh(contest)
    return contest
