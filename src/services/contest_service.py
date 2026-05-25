from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from crud import contest_crud, contest_access_crud, task_crud, solution_crud
from schemas import contest_schemas
from database.models.base import (
    User,
    Contest,
    ContestAccess,
    SolutionStatusEnum,
    Solution,
    UserStatusEnum,
)


async def get_solutions_points(
    db: AsyncSession, user_id: UUID, task_id: UUID
) -> SolutionStatusEnum | None:
    solutions: list[Solution] = await solution_crud.get_solutions(db, user_id, task_id)
    if not len(solutions):
        return None
    points: list[SolutionStatusEnum] = [solution.points for solution in solutions]
    if len(points) == 0:
        return 0
    else:
        return max(points)


async def get_contest_info(  # contest/(slug:str)/
    db: AsyncSession, user: User, contest_slug: str
) -> dict:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest: Contest | None = await contest_crud.get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contest not found"
        )

    contest_response: contest_schemas.ContestInfoResponse = (
        contest_schemas.ContestInfoResponse(
            name=contest.name,
            description=contest.description,
            tasks=[
                contest_schemas.TaskInContestResponse(
                    name=task.name,
                    slug=task.slug,
                    points=get_solutions_points(db, user.id, task.id),
                )
                for task in await task_crud.get_tasks_by_contest_id(db, contest.id)
            ],
            is_curator=False,
            is_activ=contest.is_active,
        )
    )

    if contest.curator_id == user.id:
        contest_response["is_curator"] = True
        return contest_response

    if not contest.is_active and contest.is_public:
        contest_response["tasks"] = None
        return contest_response
    access: (
        ContestAccess | None
    ) = await contest_access_crud.get_access_by_user_and_contest(
        db, user.id, contest.id
    )

    if not contest.is_active or access is None and not contest.is_public:
        raise HTTPException(
            status_code=403, detail="You do not have access to this contest"
        )
    else:
        return contest_response


async def create_contest(
    db: AsyncSession, user: User, data: contest_schemas.CreateContestInput
) -> dict:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    if user.status != UserStatusEnum.CURATOR:
        raise HTTPException(status_code=403, detail="The user is not a curator")

    if await contest_crud.get_contest_by_slug(db, data.slug) is not None:
        raise HTTPException(status_code=409, detail="There is a contest with this slug")

    contest = Contest(
        name=data.name,
        curator_id=user.id,
        slug=data.slug,
        description=data.description,
        is_active=False,
        is_public=data.is_public,
        is_ended=False,
    )
    contest = await contest_crud.add_contest(db, contest)


async def edit_contest(
    db: AsyncSession,
    user: User,
    contest_slug: str,
    data: contest_schemas.EditContestInput,
) -> dict:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest = await contest_crud.get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(status_code=404, detail="Contest not found")

    if contest.curator_id != user.id:
        raise HTTPException(
            status_code=403, detail="You do not have access to this contest"
        )

    contest = await contest_crud.update_contest(
        db,
        contest,
        name=data.contest_name,
        is_active=data.is_active,
        is_public=data.is_public,
    )

    return await get_contest_info(db, user, contest_slug)


async def delete_contest(db: AsyncSession, user: User, contest_slug: str) -> None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    contest = await contest_crud.get_contest_by_slug(db, contest_slug)
    if contest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contest not found"
        )

    if contest.curator_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this contest",
        )

    await contest_crud.delete_contest_from_db(db, contest)
