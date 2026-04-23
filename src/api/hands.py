import uuid
from database.core.db import get_db
from database.models.base import User,UserStatusEnum
async def login(name:str,login:str,password:str,status:UserStatusEnum ) -> uuid.UUID|None:
    new_user = {



    }