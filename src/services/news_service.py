from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.base import News, User, UserStatusEnum
from crud import news_crud
from schemas import news_schemas

async def get_list_of_last_news(db:AsyncSession, last:str|None):
    if last is None:
        news:list[News] = news_crud.get_the_last_news(db,5)
    else:
        last_news: News|None = await news_crud.get_news_by_slug(db,last)
        if last_news is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="News not found"
            )
        news:list[News] = news_crud.get_the_last_news_after_a_certain_time(db,last_news.created_at,5)
    
    return news_schemas.ListOfNewsInfoResponse(
        news=[news_schemas.NewsInfoResponse(
            name=i_news.name,
            slug=i_news.slug,
            text=i_news.text,
            )
            for i_news in news
        ],
        quantity=len(news)
    )
    
async def get_news(db:AsyncSession, slug:str) -> news_schemas.NewsInfoResponse:
    news: News|None = await news_crud.get_news_by_slug(db,slug)
    if news is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="News not found"
        )
    return news_schemas.NewsInfoResponse(
        name=news.name,
        slug=news.slug,
        text=news.text,
    )

async def create_news(db:AsyncSession, user:User, data:news_schemas.CreateNewsInput)->None:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    
    if user.status != UserStatusEnum.CURATOR:
        print(user.status)
        raise HTTPException(status_code=403, detail="The user is not a curator")

    if await news_crud.get_news_by_slug(db, data.slug) is not None:
        raise HTTPException(status_code=409, detail="There is a news with this slug")

    news: News = News(
        slug=data.slug,
        name=data.name,
        text=data.text,
        curator_id=user.id,
    )
    news = await news_crud.add_news(db, news)


