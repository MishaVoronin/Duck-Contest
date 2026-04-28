from sqlalchemy.ext.asyncio import AsyncSession
from database.models.base import RefreshToken


async def create_refresh_token(db: AsyncSession, token: RefreshToken) -> RefreshToken:
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token
