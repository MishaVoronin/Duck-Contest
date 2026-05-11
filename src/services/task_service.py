from sqlalchemy.ext.asyncio import AsyncSession
from crud.contest import get_contest_by_slug
from crud.contest_access import get_access_by_user_and_contest
from crud.task import (
    get_task_by_slug_and_contest_id,
    add_task,
    delete_task_from_bd,
    update_task,
)
from database.models.base import User, Task
from schemas.task import CreateTaskInput, EditTaskInput
from fastapi import HTTPException


async def get_task_info(
    db: AsyncSession, user: User, contest_slug: str, task_slug: str
) -> dict:
    contest = await get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(status_code=404, detail="Contest not found")

    task = await get_task_by_slug_and_contest_id(db, task_slug, contest.id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task_dict = {
        "name": task.name,
        "text": task.text,
        "is_curator": contest.curator_id == user.id,
    }

    if contest.curator_id == user.id:
        return task_dict

    access = await get_access_by_user_and_contest(db, user.id, contest.id)

    if not contest.is_active:
        raise HTTPException(status_code=404, detail="Contest is not active")

    if not contest.is_public and access is None:
        raise HTTPException(
            status_code=403, detail="You do not have access to this contest"
        )

    return task_dict


async def create_task(
    db: AsyncSession, user: User, contest_slug: str, data: CreateTaskInput
) -> dict:
    contest = await get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(status_code=404, detail="Contest not found")
    if contest.curator_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if await get_task_by_slug_and_contest_id(db, data.slug, contest.id) is not None:
        raise HTTPException(
            status_code=409, detail="Task with this slug already exists in contest"
        )

    task = Task(
        contest_id=contest.id,
        slug=data.slug,
        name=data.name,
        text=data.text,
        answer=data.answer,
    )
    task = await add_task(db, task)

    return await get_task_info(db, user, contest_slug, task.slug)


async def edit_task(
    db: AsyncSession, user: User, contest_slug: str, task_slug: str, data: EditTaskInput
) -> dict:
    contest = await get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(status_code=404, detail="Contest not found")
    if contest.curator_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    task = await get_task_by_slug_and_contest_id(db, task_slug, contest.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task = await update_task(db, task, data.name, data.text, data.answer)
    return await get_task_info(db, user, contest_slug, task.slug)


async def delete_task(
    db: AsyncSession, user: User, contest_slug: str, task_slug: str
) -> None:
    contest = await get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(status_code=404, detail="Contest not found")
    if contest.curator_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    task = await get_task_by_slug_and_contest_id(db, task_slug, contest.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await delete_task_from_bd(db, task)
    return None
