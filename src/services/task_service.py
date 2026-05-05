from sqlalchemy.ext.asyncio import AsyncSession
from crud.contest import get_contest_by_slug
from crud.contest_access import get_access_by_user_and_contest
from crud.task import (
    get_task_by_slug_and_contest_id,
    add_task,
    delete_task_from_bd,
    update_task,
)
from database.models.base import User, Contest, Task, ContestAccess


async def get_task_info(  # contest/(slug:str)/task/(slug:str)/
    db: AsyncSession, user: User, contest_slug: str, task_slug: str
) -> dict | str:
    contest: Contest | None = await get_contest_by_slug(db, contest_slug)

    if contest is None:
        return "404 contest not found"

    task: Task | None = await get_task_by_slug_and_contest_id(db, task_slug, contest.id)

    task_dict: dict = {"name": task.name, "text": task.text, "is_curator": False}

    if task is None:
        return "404 task is not found"

    if contest.curator_id is user.id:
        task_dict["is_curator"] = True
        return task_dict

    if contest.is_public:
        return task_dict

    access: ContestAccess | None = await get_access_by_user_and_contest(
        db, user.id, contest.id
    )

    if access is None:
        return "404 contest not found"
    else:
        return task_dict


async def create_task(  # contest/(slug:str)/task/set
    db: AsyncSession,
    user: User,
    contest_slug: str,
    task_slug: str,
    task_name: str,
    task_text: str,
    task_test: dict,
) -> Task | str:
    contest: Contest | None = await get_contest_by_slug(db, contest_slug)

    if contest is None:
        return "404 contest not found"

    if contest.curator_id is not user.id:
        return "403 You do not have access this contest"

    if await get_task_by_slug_and_contest_id(db, task_slug, contest.id) is not None:
        return "There is a task with this slug in this contest"

    task: Task = Task(
        contest_id=contest.id,
        slug=task_slug,
        name=task_name,
        text=task_text,
        test=task_test,
    )

    task = await add_task(db, task)
    return get_task_info(db, user, contest_slug)


async def edit_task(  # contest/(slug:str)/task/(slug:str)/edit
    db: AsyncSession,
    user: User,
    contest_slug: str,
    task_slug: str,
    task_name: str,
    task_text: str,
    task_test: dict,
) -> Task | str:
    contest: Contest | None = await get_contest_by_slug(db, contest_slug)

    if contest is None:
        return "404 contest not found"

    if contest.curator_id is not user.id:
        return "403 You do not have access this contest"

    task: Task | None = await get_task_by_slug_and_contest_id(db, task_slug, contest.id)
    if task is None:
        return "404 task not found"

    task = await update_task(db, task, task_name, task_text, task_test)
    return get_task_info(db, user, contest_slug)


async def delete_task(  # contest/(slug:str)/task/(slug:str)/delete
    db: AsyncSession, user: User, contest_slug: str, task_slug: str
) -> str:
    contest: Contest | None = await get_contest_by_slug(db, contest_slug)

    if contest is None:
        return "404 contest not found"

    if contest.curator_id is not user.id:
        return "403 You do not have access this contest"

    task: Task | None = await get_task_by_slug_and_contest_id(db, task_slug, contest.id)
    if task is None:
        return "404 task not found"

    await delete_task_from_bd(db, task)
    return "200 task is deleted"
