from sqlalchemy.ext.asyncio import AsyncSession
from database.models.base import Solution
from sqlalchemy import select
from uuid import UUID

async def add_solution(db: AsyncSession, solution: Solution) -> Solution:
    db.add(solution)
    await db.commit()
    await db.refresh(solution)
    return solution

async def get_solutions(db: AsyncSession, user_id:UUID ,task_id: UUID) -> list[Solution]:
    result = await db.execute(select(Solution).where(Solution.task_id == task_id,Solution.user_id == user_id))
    return result.scalars().all()