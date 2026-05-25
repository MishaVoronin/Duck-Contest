from fastapi import HTTPException, status

from database.models.base import (
    User,
    ContestAccess,
    Solution,
    SolutionStatusEnum,
)
from sqlalchemy.ext.asyncio import AsyncSession
from crud import contest_crud, contest_access_crud, task_crud, solution_crud


async def task_solution(
    db: AsyncSession, user: User, contest_slug: str, task_slug: str, answer: str
) -> SolutionStatusEnum:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest = await contest_crud.get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(status_code=404, detail="Contest not found")

    access: (
        ContestAccess | None
    ) = await contest_access_crud.get_access_by_user_and_contest(
        db, user.id, contest.id
    )
    if not contest.is_public and contest.curator_id != user.id and access is None:
        raise HTTPException(
            status_code=403, detail="You do not have access to this contest"
        )

    task = await task_crud.get_task_by_slug_and_contest_id(db, task_slug, contest.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    solution = Solution(
        user_id=user.id,
        task_id=task.id,
        answer=answer.strip(),
        status=(
            SolutionStatusEnum.OK
            if answer.strip() == task.answer
            else SolutionStatusEnum.WA
        ),
    )

    saved_solution = await solution_crud.add_solution(db, solution)
    return {"status": saved_solution.status}
