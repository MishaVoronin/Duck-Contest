from database.models.base import User, ContestAccess, Task
from sqlalchemy.ext.asyncio import AsyncSession

async def task_solution(  # contest/(slug:str)/task/(slug:str)/solution
    db: AsyncSession, user: User, contest_slug: str, task_slug: str
) -> dict | str:
    ...