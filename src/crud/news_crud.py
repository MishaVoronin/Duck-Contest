from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, DateTime
from database.models.base import News


async def add_news(db: AsyncSession, news: News) -> News:
    db.add(news)
    await db.commit()
    await db.refresh(news)
    return news


async def get_news_by_slug(db: AsyncSession, slug: str) -> News | None:
    result = await db.execute(select(News).where(News.slug == slug))
    return result.scalar_one_or_none()


async def get_the_last_news(db: AsyncSession, limit: int) -> News | None:
    result = await db.execute(
        select(News).order_by(News.created_at.desc()).limit(limit)
    )
    return result.scalar_one_or_none()


async def get_the_last_news_after_a_certain_time(
    db: AsyncSession, time: DateTime, limit: int
) -> News | None:
    result = await db.execute(
        select(News)
        .where(News.created_at < time)
        .order_by(News.created_at.desc())
        .limit(limit)
    )
    return result.scalar_one_or_none()
