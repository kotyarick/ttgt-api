from typing import Type, TypeVar, Optional, List

import fastapi
from fastapi import HTTPException
from pydantic import BaseModel

from models.database import DatabaseNews, DatabaseTeacher, NewsType, NewsStatus, DatabaseAdmin
from utils import smart_crop, crop_first_paragraph

IN = TypeVar('IN', bound='IncompleteNews')
PN = TypeVar('PN', bound='PublicNews')
PR = TypeVar('PR', bound='PrivateNews')
A = TypeVar('A', bound='Admin')

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

    type: int

    images: List[str]

    @classmethod
    def from_database(cls: Type[IN], data: DatabaseNews) -> IN:
        return IncompleteNews(
            id = data.id,
            slug = data.slug,
            title = data.title,
            text = crop_first_paragraph(data.body),
            publish_date= round(float(data.publish_date.timestamp())),
            type=data.type,
            images=data.images.split("\n")
        )


class PublicNews(BaseModel):
    """
    Полная новость техникума
    """

    id: int

    # image_amount: int
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

    type: int
    author: str

    images: List[str]

    @classmethod
    def from_database(cls: Type[PN], data: DatabaseNews) -> PN:
        return PublicNews(
            id = data.id,
            images = data.images.split("\n"),
            slug = data.slug,
            title = data.title,
            text = data.body,
            publish_date= data.publish_date.timestamp(),
            type=data.type,
            author=data.author
        )

class PostableNews(BaseModel):
    """ Новость, которую можно опубликовать """

    slug: str
    title: str = ""
    body: str = ""
    publish_date: int
    author: str = ""
    type: NewsType = NewsType.News
    status: NewsStatus = NewsStatus.Draft

    def check(self):
        try:
            assert 0 < len(self.slug) <= 15, "slug должен быть не пустым и не длиннее 15 символов"
            assert self.title != "", "Поле slug обязательно"
            assert self.body != "", "Поле title обязательно"
            assert self.author != "", "Поле body обязательно"
            assert 0 <= self.type.value <= 3, "Тип поста должен быть в диапазоне 0-3"
            assert 0 <= self.status.value <= 1, "Статус поста должен быть в диапазоне 0-1"
        except AssertionError as error:
            raise HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )

class PrivateNews(BaseModel):
    """ Новость + приватные данные """
    id: int
    slug: str
    title: str
    body: str
    publish_date: int
    images: List[str]
    author: str
    type: NewsType
    status: NewsStatus

    @classmethod
    def from_database(cls: Type[PR], data: DatabaseNews) -> PR:
        return PrivateNews(
            id = data.id,
            slug = data.slug,
            title = data.title,
            body = data.body,
            publish_date = round(float(data.publish_date.timestamp())),
            images = data.images.split("\n"),
            author = data.author,
            type = data.type,
            status = data.status
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

    middle_name: str = ""
    """ Отчество """

    password_hash: str

    @classmethod
    def from_database(cls: Type[A], data: DatabaseAdmin) -> A:
        return Admin(
            id=data.id,
            first_name=data.first_name,
            second_name=data.second_name,
            middle_name=data.middle_name,
            password_hash=data.password_hash
        )

class Teacher(BaseModel):
    """
    Преподаватель.
    """

    id: int

    initials: str
    """ Инициалы """

    @classmethod
    def from_database(cls, data: DatabaseTeacher):
        return Teacher(
            id=data.id,
            initials=data.initials
        )

class CreateTeacher(BaseModel):
    first_name: str
    """ Имя """

    second_name: str
    """ Фамилия """

    middle_name: str = ""
    """ Отчество """

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