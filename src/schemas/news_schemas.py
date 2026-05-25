from pydantic import BaseModel, StringConstraints
from typing import Annotated


class CreateNewsInput(BaseModel):
    name: str
    slug: str
    text: str


class NewsInfoResponse(BaseModel):
    name: Annotated[
        str,
        StringConstraints(
            min_length=10,
            max_length=100,
            strip_whitespace=True,
        ),
    ]
    slug: Annotated[
        str,
        StringConstraints(
            pattern=r"^[0-9a-zA-Z\-_]+$",
            min_length=1,
            max_length=100,
            strip_whitespace=True,
        ),
    ]
    text: Annotated[
        str,
        StringConstraints(
            min_length=50,
            max_length=1000,
            strip_whitespace=True,
        ),
    ]


class ListOfNewsInfoResponse(BaseModel):
    news: list[NewsInfoResponse]
    quantity: int
