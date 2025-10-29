import asyncio
import os.path
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi import status
from sqlalchemy import select

from api_tags import POSTS, ADMIN_ONLY
from database import Session
from models.api import PrivatePost, PostablePost, IncompletePost, Event
from models.database import DatabasePost, PostStatus
from routes.admin import AdminRequired
from routes.websocket import broadcast_event

posts_router = APIRouter(prefix="/posts", tags=[POSTS, ADMIN_ONLY])

async def on_post_create_or_update(post: IncompletePost, is_public: bool):
    asyncio.create_task(cleanup_files())

    if is_public:
        await broadcast_event(Event(
            newPost=post
        ))

async def cleanup_files():
    with Session.begin() as session:
        files: List[str] = session.scalars(
            select(DatabasePost.files)
        ).all()

        database_files = [
            file
            for file in "\n".join(files).split("\n")
        ]

        real_files = os.listdir("database_files")

        counter = 0

        for real_file in real_files:
            if not real_file in database_files:
                os.remove(f"database_files/{real_file}")
                counter += 1

        if counter > 0:
            print(f"Удалено не используемых файлов: {counter}")

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
            files="\n".join(post.files),
            author=post.author,
            type=post.type,
            status=post.status,
            category=post.category
        )
        session.add(post)
        session.flush()
        await on_post_create_or_update(
            IncompletePost.from_database(post),
            post.status == PostStatus.Published.value
        )
        return PrivatePost.from_database(post)


@posts_router.patch("/{post_id:int}", name="Отредактировать пост")
async def edit_post(
        post: PostablePost,
        post_id: int
) -> PrivatePost:
    post.check()

    with Session.begin() as session:
        original_post = (
            session
                .scalar(
                    select(DatabasePost)
                        .where(DatabasePost.id == post_id)
                )
        )
        if original_post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        prevStatus = original_post.status

        dump = post.model_dump()
        dump["publish_date"] = datetime.fromtimestamp(dump["publish_date"])
        dump["files"] = "\n".join(post.files)

        (
            session
            .query(DatabasePost)
            .where(DatabasePost.id == post_id)
            .update(dump)
        )

        session.flush()
        post = session.scalar(
            select(DatabasePost).where(DatabasePost.id == post_id)
        )

        asyncio.create_task(
            on_post_create_or_update(
                IncompletePost.from_database(post),
                post.status == PostStatus.Published.value
            )
        )

        if (prevStatus == PostStatus.Published.value
                and post.status == PostStatus.Draft):
            asyncio.create_task(
                broadcast_event(
                    Event(
                        removePost=post_id
                    )
                )
            )

        return PrivatePost.from_database(post)


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

    await broadcast_event(Event(
        removePost=post_id
    ))

    await cleanup_files()

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
