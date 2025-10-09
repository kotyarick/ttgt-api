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
from routes.auth import admin_login

adminRouter = APIRouter(prefix="/admin")

AdminRequired = Annotated[Admin, Depends(admin_login)]

@adminRouter.get("/super-secret")
async def get_super_secret_data(
        admin: AdminRequired
) -> dict[str, str]:
    print(admin)
    return { "data": "У тебя получилось" }

@adminRouter.post("/news")
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
                image_amount = 0,
                author = news.author or f"{admin.second_name} {admin.first_name[0]}. {
                    (admin.middle_name[0] + '.') if admin.middle_name else ''
                }",
                type = news.type,
                status = news.status
            )
        try:
            session.add(new)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        return PrivateNews.from_orm(
            session.scalar(
                select(DatabaseNews).where(DatabaseNews.slug == news.slug)
            )
        )

@adminRouter.patch("/news/{news_id:int}")
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


        return PrivateNews.from_orm(session.scalar(
            select(DatabaseNews).where(DatabaseNews.id == news_id)
        ))

@adminRouter.delete("/news/{news_id:int}")
async def delete_news(
        admin: AdminRequired,
        news_id: int
):
    ...