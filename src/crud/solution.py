from sqlalchemy.ext.asyncio import AsyncSession
from database.models.base import Solution


async def add_solution(db: AsyncSession, solution: Solution) -> Solution:
    db.add(solution)
    await db.commit()
    await db.refresh(solution)
    return solution
