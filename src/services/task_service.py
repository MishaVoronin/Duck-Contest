from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from crud import contest_crud, contest_access_crud, solution_crud, task_crud 
from schemas import task_schemas
from database.models.base import User, Task, Solution


async def get_task_info(
    db: AsyncSession, user: User, contest_slug: str, task_slug: str
) -> dict:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest = await contest_crud.get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(status_code=404, detail="Contest not found")

    task = await task_crud.get_task_by_slug_and_contest_id(db, task_slug, contest.id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    solutions: list[Solution] = await solution_crud.get_solutions(db, user.id, task.id)
    task_dict = task_schemas.TaskInfoResponse(
        name=task.name,
        text=task.text,
        solutions=[
            task_schemas.SolutionsInTaskResponse(
                status=solution.status,
                answer=solution.answer,
                points=solution.points,
                submitted_at=solution.submitted_at.isoformat(),
            )
            for solution in solutions
        ],
        is_curator=contest.curator_id == user.id,
    )

    if contest.curator_id == user.id:
        return task_dict

    access = await contest_access_crud.get_access_by_user_and_contest(db, user.id, contest.id)

    if not contest.is_active:
        raise HTTPException(status_code=404, detail="Contest is not active")

    if not contest.is_public and access is None:
        raise HTTPException(
            status_code=403, detail="You do not have access to this contest"
        )

    return task_dict


async def create_task(
    db: AsyncSession, user: User, contest_slug: str, data: task_schemas.CreateTaskInput
) -> dict:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest = await contest_crud.get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(status_code=404, detail="Contest not found")
    if contest.curator_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if await task_crud.get_task_by_slug_and_contest_id(db, data.slug, contest.id) is not None:
        raise HTTPException(
            status_code=409, detail="Task with this slug already exists in contest"
        )

    task = Task(
        contest_id=contest.id,
        slug=data.slug,
        name=data.name,
        text=data.text,
        answer=data.answer.strip(),
        points=data.points,
    )
    task = await task_crud.add_task(db, task)

    return await get_task_info(db, user, contest_slug, task.slug)


async def edit_task(
    db: AsyncSession, user: User, contest_slug: str, task_slug: str, data: task_schemas.EditTaskInput
) -> dict:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest = await contest_crud.get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(status_code=404, detail="Contest not found")
    if contest.curator_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    task = await task_crud.get_task_by_slug_and_contest_id(db, task_slug, contest.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task = await task_crud.update_task(db, task, data.name, data.text, data.answer)
    return await get_task_info(db, user, contest_slug, task.slug)


async def delete_task(
    db: AsyncSession, user: User, contest_slug: str, task_slug: str
) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest = await contest_crud.get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(status_code=404, detail="Contest not found")
    if contest.curator_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    task = await task_crud.get_task_by_slug_and_contest_id(db, task_slug, contest.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await task_crud.delete_task_from_bd(db, task)
    return None
