from pydantic import BaseModel, StringConstraints
from typing import Annotated

SlugType = Annotated[
    str,
    StringConstraints(
        pattern=r"^[a-zA-Z\-_]+$", min_length=1, max_length=255, strip_whitespace=True
    ),
]


class CreateContestInput(BaseModel):
    name: str
    slug: SlugType
    text: str
    is_public: bool = True


class EditContestInput(BaseModel):
    contest_name: str
    is_active: bool
    is_public: bool


class ContestInfoResponse(BaseModel):
    name: str
    tasks: list[str]
    is_curator: bool
