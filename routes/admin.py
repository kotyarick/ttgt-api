from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from fastapi import status

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
                post_type = news.post_type,
                post_status = news.post_status
            )
        try:
            session.add(new)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
        return PrivateNews.from_orm(new)

@adminRouter.patch("/news/{post_id:int}")
async def edit_news(
        admin: AdminRequired,
        news: PostableNews,
        post_id: int
):
    with Session.begin() as session:
        pass