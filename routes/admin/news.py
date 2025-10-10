from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import status

from database import Session
from models.api import PrivateNews, PostableNews
from models.database import DatabaseNews
from routes.admin import AdminRequired

newsRouter = APIRouter(prefix="/news")

@newsRouter.post("/")
async def create_news(
        _admin: AdminRequired,
        news: PostableNews
) -> PrivateNews:
    news.check()

    with Session.begin() as session:
        new = DatabaseNews(
                slug = news.slug,
                title = news.title,
                body = news.body,
                publish_date = datetime.fromtimestamp(news.publish_date),
                #TODO: кол-во картинок
                image_amount = 0,
                author = news.author,
                type = news.type,
                status = news.status
            )
        try:
            session.add(new)
            session.flush()
            return PrivateNews.from_database(new)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

@newsRouter.patch("/{news_id:int}")
async def edit_news(
        _admin: AdminRequired,
        news: PostableNews,
        news_id: int
) -> PrivateNews:
    news.check()

    with Session.begin() as session:
        if session.scalar(select(DatabaseNews).where(DatabaseNews.id == news_id)) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        dump = news.model_dump()
        dump["publish_date"] = datetime.fromtimestamp(dump["publish_date"])

        (
            session
                .query(DatabaseNews)
                .filter(DatabaseNews.id == news_id)
                .update(dump)
        )


        return PrivateNews.from_database(session.scalar(
            select(DatabaseNews).where(DatabaseNews.id == news_id)
        ))

@newsRouter.delete(
    "/{news_id:int}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_news(
        _admin: AdminRequired,
        news_id: int
):
    with Session.begin() as session:
        (
            session
                .query(DatabaseNews)
                .filter(DatabaseNews.id == news_id)
                .delete()
        )

@newsRouter.get("/", name="Получить список всех новостей")
async def get_news_list(
        offset: int = 0,
        limit: int = 10
) -> List[PrivateNews]:
    limit = min(limit, 15)

    with Session.begin() as session:
        # noinspection PyTypeChecker
        news: List[DatabaseNews] = session.scalars(
            select(DatabaseNews).offset(offset).limit(limit)
        ).all()

        return [
            PrivateNews.from_database(new)
            for new in news
        ]

@newsRouter.get("/{slug:str}", name="Получить новость")
async def get_news(slug: str) -> PrivateNews:
    with Session.begin() as session:
        try:
            # noinspection PyTypeChecker
            news = session.scalar(
                select(DatabaseNews).where(DatabaseNews.slug == slug)
            )

            print(news.id)

            return PrivateNews.from_database(news)
        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)