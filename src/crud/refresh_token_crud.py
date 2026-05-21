from sqlalchemy.ext.asyncio import AsyncSession
from database.models.base import RefreshToken
from sqlalchemy import select
from datetime import datetime, timezone


async def save_refresh_token(db: AsyncSession, token: RefreshToken) -> RefreshToken:
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token


async def get_refresh_token_by_jwt(db: AsyncSession, token: str):
    res = await db.execute(select(RefreshToken).where(RefreshToken.token == token))
    return res.scalar_one_or_none()


async def revoke_token(db: AsyncSession, rt: RefreshToken):
    rt.is_revoked = True
    rt.revoked_at = datetime.now(timezone.utc)
    await db.commit()
