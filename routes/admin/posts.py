from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi import status
from sqlalchemy import select

from api_tags import POSTS, ADMIN_ONLY
from database import Session
from models.api import PrivatePost, PostablePost
from models.database import DatabasePost
from routes.admin import AdminRequired

posts_router = APIRouter(prefix="/posts", tags=[POSTS, ADMIN_ONLY])


@posts_router.post("/", name="Создать пост")
async def create_post(
        _admin: AdminRequired,
        post: PostablePost
) -> PrivatePost:
    """ Создать пост

    Если статус поста Draft, то он не будет видна на главной странице
    """
    post.check()

    with Session.begin() as session:
        post = DatabasePost(
            title=post.title,
            body=post.body,
            publish_date=datetime.fromtimestamp(post.publish_date),
            images="\n".join(post.images),
            author=post.author,
            type=post.type,
            status=post.status,
            category=post.category
        )
        session.add(post)
        session.flush()
        return PrivatePost.from_database(post)


@posts_router.patch("/{post_id:int}", name="Отредактировать пост")
async def edit_post(
        post: PostablePost,
        post_id: int
) -> PrivatePost:
    post.check()

    with Session.begin() as session:
        if (
                session
                        .scalar(
                    select(DatabasePost)
                            .where(DatabasePost.id == post_id)
                )
        ) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        dump = post.model_dump()
        dump["publish_date"] = datetime.fromtimestamp(dump["publish_date"])
        dump["images"] = "\n".join(post.images)

        (
            session
            .query(DatabasePost)
            .where(DatabasePost.id == post_id)
            .update(dump)
        )

        session.flush()
        return PrivatePost.from_database(session.scalar(
            select(DatabasePost).where(DatabasePost.id == post_id)
        ))


@posts_router.get("/", name="Получить список всех постов")
async def get_post_list(
        category: int,
        offset: int = 0,
        limit: int = 10,
) -> List[PrivatePost]:
    """
    В отличие от GET /content/posts, этот endpoint даст неопубликованные посты
    """
    limit = min(limit, 100)

    with Session.begin() as session:
        # noinspection PyTypeChecker
        posts: List[DatabasePost] = session.scalars(
            select(DatabasePost).where(DatabasePost.category == category).offset(offset).limit(limit)
        ).all()

        return [
            PrivatePost.from_database(post)
            for post in posts
        ]


@posts_router.delete(
    "/{post_id:int}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="Удалить пост"
)
async def delete_post(
        post_id: int
):
    with Session.begin() as session:
        (
            session
            .query(DatabasePost)
            .filter(DatabasePost.id == post_id)
            .delete()
        )


@posts_router.get("/{post_id:int}", name="Получить пост")
async def get_post(
        post_id: int
) -> PrivatePost:
    """
    В отличие от GET /content/posts, этот endpoint даст неопубликованный пост
    """
    with Session.begin() as session:
        try:
            # noinspection PyTypeChecker
            post = session.scalar(
                select(DatabasePost).where(DatabasePost.id == post_id)
            )

            print(post.id)

            return PrivatePost.from_database(post)
        except:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
