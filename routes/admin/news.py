from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import status
from sqlalchemy.sql.expression import update

from database import Session
from models.api import PrivateNews, PostableNews, Admin
from models.database import DatabaseNews
from routes.admin import AdminRequired
from utils import initials

newsRouter = APIRouter(prefix="/news")

@newsRouter.post("/")
async def create_news(
        admin: AdminRequired,
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
        admin: AdminRequired,
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
        admin: AdminRequired,
        news_id: int
):
    with Session.begin() as session:
        (
            session
                .query(DatabaseNews)
                .filter(DatabaseNews.id == news_id)
                .delete()
        )

