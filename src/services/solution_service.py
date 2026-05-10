from database.models.base import (
    User,
    ContestAccess,
    Task,
    Contest,
    Solution,
    SolutionStatusEnum,
)
from sqlalchemy.ext.asyncio import AsyncSession
from crud.contest import get_contest_by_slug
from crud.contest_access import get_access_by_user_and_contest
from crud.task import get_task_by_slug_and_contest_id
from crud.solution import add_solution


async def task_solution(  # contest/(slug:str)/task/(slug:str)/solution
    db: AsyncSession, user: User, contest_slug: str, task_slug: str, answer: str
) -> SolutionStatusEnum | str:
    contest: Contest | None = await get_contest_by_slug(db, contest_slug)

    if contest is None:
        return "404 contest not found"

    access: ContestAccess | None = await get_access_by_user_and_contest(
        db, user.id, contest.id
    )

    if access is None and user.id is not contest.id and not contest.is_public:
        return "403 You do not have access this contest"

    task: Task | None = await get_task_by_slug_and_contest_id(db, task_slug, contest.id)

    if task is None:
        return "404 task is not found"

    solution: Solution = Solution(
        user_id=user.id,
        contest_id=contest.id,
    )
    if answer is task.answer:
        solution.status = SolutionStatusEnum.OK
    else:
        solution.status = SolutionStatusEnum.WA

    solution = await add_solution(db, solution)

    return solution.status
