from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from fastapi import status

from database import Session
from models.api import IncompleteNews, PublicNews
from models.database import DatabaseNews, NewsStatus
import traceback

contentRoutes = APIRouter(prefix="/content")

@contentRoutes.get("/news", name="Получить список новостей")
async def get_news_list(
        offset: int = 0,
        limit: int = 10
) -> List[IncompleteNews]:
    limit = min(limit, 15)

    with Session.begin() as session:
        # noinspection PyTypeChecker
        news: List[DatabaseNews] = session.scalars(
            select(DatabaseNews).where(DatabaseNews.status == NewsStatus.Published).offset(offset).limit(limit)
        ).all()

        return [
            IncompleteNews.from_database(new)
            for new in news
        ]

@contentRoutes.get("/news/{slug:str}", name="Получить новость")
async def get_news(slug: str) -> PublicNews:
    with Session.begin() as session:
        try:
            # noinspection PyTypeChecker
            news = session.scalar(
                select(DatabaseNews).where(DatabaseNews.status == NewsStatus.Published and DatabaseNews.slug == slug)
            )

            print(news.id)

            return PublicNews.from_database(news)
        except:
            print(traceback.format_exc())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)