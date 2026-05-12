from sqlalchemy.ext.asyncio import AsyncSession
from crud.contest import get_contest_by_slug
from crud.contest_access import add_access, get_access_by_user_and_contest
from crud.user import get_user_by_name
from database.models.base import User, Contest, ContestAccess


async def create_contest_access(
    db: AsyncSession, user: User, slug: str, user_name: str
) -> ContestAccess | str:
    contest: Contest | None = await get_contest_by_slug(db, slug)
    if contest is None:
        return "404 contest not found"

    if user.id is not contest.curator_id:
        return "403 You do not have access this contest"

    added_user: ContestAccess | None = await get_user_by_name(db, user_name)
    if added_user is None:
        return "404 user not found"

    access = await get_access_by_user_and_contest(db, added_user.id, contest.id)
    if access is not None:
        return "access already exists"

    return await add_access(ContestAccess(user_id=added_user.id, contest_id=contest.id))
