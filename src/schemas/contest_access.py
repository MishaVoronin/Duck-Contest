from pydantic import BaseModel, StringConstraints
from typing import Annotated
from database.models.base import SolutionStatusEnum

class CreateAccessInput(BaseModel):
    user:str
    