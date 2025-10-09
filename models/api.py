from typing import Optional, Any, Self

import fastapi
from fastapi import HTTPException
from pydantic import BaseModel

from models.database import DatabaseNews, DatabaseAdmin, PostType, PostStatus
from utils import smart_crop


class IncompleteNews(BaseModel):
    """
    Неполная новость техникума, отправляется в списке.
    """
    id: int

    slug: str
    """
    User-friendly ID.
    """

    title: str
    """
    Заголовок новости.
    """

    text: str
    """
    Первые несколько предложений.
    """

    publish_date: int
    """
    Timestamp создания
    """

    post_type: int

    def from_orm(obj: DatabaseNews) -> Self:
        return IncompleteNews(
            id = obj.id,
            slug = obj.slug,
            title = obj.title,
            text = smart_crop(obj.body, 100),
            publish_date= round(float(obj.publish_date.timestamp())),
            post_type=obj.post_type
        )


class PublicNews(BaseModel):
    """
    Полная новость техникума
    """

    id: int

    image_amount: int
    """
    Количество картинок.
    Получить картинку: GET /news/{slug}/{index}.png
    """

    slug: str
    """
    User-friendly ID.
    """

    title: str
    """
    Заголовок новости.
    """

    text: str
    """
    Текст новости.
    """

    publish_date: int
    """
    Timestamp создания
    """

    post_type: int
    author: str

    def from_orm(obj: DatabaseNews) -> Self:
        return PublicNews(
            id = obj.id,
            image_amount = obj.image_amount,
            slug = obj.slug,
            title = obj.title,
            text = obj.body,
            publish_date= obj.publish_date.timestamp(),
            post_type=int(obj.post_type),
            author=obj.author
        )

class PostableNews(BaseModel):
    """ Новость, которую можно запостить """

    slug: str
    title: str = ""
    body: str = ""
    publish_date: int
    author: str = ""
    post_type: PostType = PostType.News
    post_status: PostStatus = PostStatus.Draft

    def validate(self):
        try:
            assert type(self.slug) == str
            assert type(self.title) == str
            assert type(self.body) == str
            assert type(self.publish_date) == int
            assert type(self.author) == str
            assert type(self.post_type) == PostType
            assert type(self.post_status) == PostStatus

            assert 0 < len(self.slug) <= 15
            assert self.title != ""
            assert self.body != ""
            assert self.author != ""
            assert 0 <= self.post_type.value <= 3
            assert 0 <= self.post_status.value <= 1
        except AssertionError as error:
            print(error)
            raise HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST)

class PrivateNews(BaseModel):
    """ Новость + приватные данные """
    id: int
    slug: str
    title: str
    body: str
    publish_date: int
    image_amount: int
    author: str
    post_type: PostType
    post_status: PostStatus

    def from_orm(obj: DatabaseNews) -> Self:
        return PrivateNews(
            id = obj.id,
            slug = obj.slug,
            title = obj.title,
            body = obj.body,
            publish_date = round(float(obj.publish_date.timestamp())),
            image_amount = obj.image_amount,
            author = obj.author,
            post_type = obj.post_type,
            post_status = obj.post_status
        )

class Admin(BaseModel):
    """
    Админ техникума.
    """

    id: int

    first_name: str
    """ Имя """

    second_name: str
    """ Фамилия """

    middle_name: str
    """ Отчество """

    def from_orm(obj: DatabaseAdmin) -> Self:
        return Admin(
            id=obj.id,
            first_name=obj.first_name,
            second_name=obj.second_name,
            middle_name=obj.middle_name
        )


class Comment(BaseModel):
    """
    Комментарий к новости
    """

    id: int

    news_id: int
    """
    ID Новости, к которой написан комментарий
    """

    sender_name: str
    """
    Кем представился отправитель
    """

    content: str
    """
    Текст комментария
    """



class Appeal(BaseModel):
    """
    Апелляция
    """

    id: int

    email: str
    phone: str
    message: str

class LoginRequest(BaseModel):
    second_name: str
    password: str

class LoginResult(BaseModel):
    token: str
    admin: Admin