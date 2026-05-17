from pydantic import BaseModel, StringConstraints
from typing import Annotated
from database.models.base import SolutionStatusEnum


class SubmitAnswerInput(BaseModel):
    answer: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)
    ]


class SubmitAnswerResponse(BaseModel):
    status: SolutionStatusEnum
