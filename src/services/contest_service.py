from sqlalchemy.ext.asyncio import AsyncSession
from crud.contest import (
    add_contest,
    get_contest_by_slug,
    delete_contest_from_db,
    update_contest,
)
from crud.contest_access import get_access_by_user_and_contest
from crud.task import get_tasks_by_contest_id
from database.models.base import User, UserStatusEnum, Contest, ContestAccess


async def get_contest_info(  # contest/(slug:str)/
    db: AsyncSession, user: User, contest_slug: str
) -> dict | str:
    contest: Contest | None = await get_contest_by_slug(db, contest_slug)
    if contest is None:
        return "404 contest not found"

    contest_dict: dict = {
        "name": contest.name,
        "tasks": await get_tasks_by_contest_id(db, contest.id),
        "is_curator": False,
    }

    if contest.curator_id == user.id:
        contest_dict["is_curator"] = True
        return contest_dict

    if not contest.is_active:
        return "404 contest not found"

    if contest.is_public:
        return contest_dict

    access: ContestAccess | None = await get_access_by_user_and_contest(
        db, user.id, contest.id
    )
    if access is None:
        return "404 contest not found"
    else:
        return contest_dict


async def create_contest(  # contest/set
    db: AsyncSession, user: User, text: str, name: str, slug: str
) -> dict | str:
    if User.status is not UserStatusEnum.CURATOR:
        return "the user is not a curator"

    if await get_contest_by_slug(db, slug) is not None:
        return "There is a contest with this slug"

    contest: Contest = Contest(name=name, slug=slug, text=text, curator_id=user.id)
    contest = await add_contest(db, contest)
    return get_contest_info(db, user, slug)


async def edit_contest(  # contest/(slug:str)/edit/
    db: AsyncSession,
    user: User,
    contest_slug: str,
    contest_name: str,
    is_active: bool,
    is_public: bool,
) -> Contest | str:
    contest: Contest | None = await get_contest_by_slug(db, contest_slug)

    if contest is None:
        return "404 contest not found"

    if contest.curator_id is not user.id:
        return "403 You do not have access this contest"

    contest = await update_contest(db, contest, contest_name, is_active, is_public)
    return get_contest_info(db, user, contest_slug)


async def delete_contest(  # contest/(slug:str)/delete
    db: AsyncSession, user: User, contest_slug: str
) -> str:
    contest: Contest | None = await get_contest_by_slug(db, contest_slug)

    if contest is None:
        return "404 contest not found"

    if contest.curator_id is not user.id:
        return "403 You do not have access this contest"

    await delete_contest_from_db(db, contest)
    return "200 contest is deleted"
