from pydantic import BaseModel, StringConstraints, Field
from typing import Annotated
from database.models.base import SolutionStatusEnum

SlugType = Annotated[
    str,
    StringConstraints(
        pattern=r"^[0-9a-zA-Z\-_]+$",
        min_length=1,
        max_length=3,
        strip_whitespace=True,
    ),
]


class CreateTaskInput(BaseModel):
    slug: SlugType
    name: Annotated[
        str,
        StringConstraints(
            min_length=10,
            max_length=100,
            strip_whitespace=True,
        ),
    ]
    text: str
    answer: Annotated[
        str,
        StringConstraints(
            min_length=1,
            strip_whitespace=True,
        ),
    ]
    points: int = Field(ge=0, le=100)


class EditTaskInput(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=10,
            max_length=100,
            strip_whitespace=True,
        ),
    ]
    text: str
    answer: str


class TaskInfoResponse(BaseModel):
    name: str
    text: str
    solutions: list[SolutionsInTaskResponse]
    is_curator: bool


class SolutionsInTaskResponse(BaseModel):
    status: SolutionStatusEnum | None
    points: int
    answer: str
    submitted_at: str
