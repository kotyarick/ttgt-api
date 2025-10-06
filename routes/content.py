from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.requests import Request
from sqlalchemy import select
from fastapi import status

from database import Session
from models.api import IncompleteNews, PublicNews
from models.database import DatabaseNews, Status

contentRoutes = APIRouter(prefix="/content")

@contentRoutes.get("/news", name="Получить список новостей")
async def get_news_list(
        offset: int = 0,
        limit: int = 10
) -> List[IncompleteNews]:
    limit = min(limit, 15)

    with Session.begin() as session:
        news: List[DatabaseNews] = session.scalars(
            select(DatabaseNews).where(DatabaseNews.post_status == Status.Published).offset(offset).limit(limit)
        ).all()

        return [
            IncompleteNews.from_orm(new)
            for new in news
        ]

@contentRoutes.get("/news/{slug:str}", name="Получить новость")
async def get_news(slug: str) -> PublicNews:
    with Session.begin() as session:
        try:
            news = session.scalar(
                select(DatabaseNews).where(DatabaseNews.post_status == Status.Published and DatabaseNews.slug == slug)
            )

            return PublicNews.from_orm(news)
        except Exception as exception:
            print(exception)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)