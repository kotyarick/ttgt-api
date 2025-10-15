from typing import List

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from fastapi import status

from database import Session
from models.api import IncompletePost, PublicPost
from models.database import DatabasePost, PostStatus
import traceback
from api_tags import CONTENT, POSTS

posts_router = APIRouter(prefix="/posts", tags=[POSTS, CONTENT])

@posts_router.get("/", name="Получить список постов")
async def get_posts_list(
        category: int,
        offset: int = 0,
        limit: int = 10
) -> List[IncompletePost]:
    limit = min(limit, 15)

    with Session.begin() as session:
        # noinspection PyTypeChecker
        posts: List[DatabasePost] = session.scalars(
            select(DatabasePost).where(
                DatabasePost.status == PostStatus.Published
                and DatabasePost.category == category
            ).offset(offset).limit(limit)
        ).all()

        return [
            IncompletePost.from_database(post)
            for post in posts
        ]

@posts_router.get("/{post_id:int}", name="Получить пост")
async def get_post(post_id: int) -> PublicPost:
    with Session.begin() as session:
        try:
            # noinspection PyTypeChecker
            post = session.scalar(
                select(DatabasePost).where(DatabasePost.id == post_id and DatabasePost.status == PostStatus.Published)
            )

            return PublicPost.from_database(post)
        except:
            print(traceback.format_exc())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
