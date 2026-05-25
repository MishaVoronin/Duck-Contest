from pathlib import Path
import sys
import  auth
import asyncio

PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from crud.user_crud import create_user
from database.models.base import User, UserStatusEnum
from database.core.db import get_db

async def main():
    db_gen = get_db()
    db = await db_gen.__anext__()
    curator = User(
        name="curator",
        login="curator",
        password=auth.hash_password("curator"),
        status=UserStatusEnum.CURATOR,   
    )
    await create_user(db,curator)

if __name__ == "__main__":
    
    asyncio.run(main())