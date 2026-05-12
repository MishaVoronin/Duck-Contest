from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models.base import Task
import uuid


async def add_task(db: AsyncSession, task: Task) -> Task:
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task_by_slug_and_contest_id(
    db: AsyncSession, slug: str, contest_id: uuid.UUID
) -> Task | None:
    result = await db.execute(
        select(Task).where(Task.slug == slug, Task.contest_id == contest_id)
    )
    return result.scalar_one_or_none()


async def get_tasks_by_contest_id(
    db: AsyncSession, contest_id: uuid.UUID
) -> list[Task]:
    result = await db.execute(select(Task).where(Task.contest_id == contest_id))
    return result.scalars().all()


async def delete_task_from_bd(db: AsyncSession, task: Task) -> None:
    await db.delete(task)
    await db.commit()


async def update_task(
    db: AsyncSession, task: Task, name: str, text: str, answer: str
) -> Task:
    task.name = name
    task.text = text
    task.answer = answer
    await db.commit()
    await db.refresh(task)
    return task
