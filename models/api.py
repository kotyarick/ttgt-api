import os.path
from typing import Type, TypeVar, Optional, List

import fastapi
from fastapi import HTTPException
from pydantic import BaseModel

from models.database import DatabasePost, DatabaseTeacher, PostStatus, DatabaseAdmin, DatabaseFile
from utils import smart_crop, crop_first_paragraph

IN = TypeVar('IN', bound='IncompletePost')
PN = TypeVar('PN', bound='PublicPost')
PR = TypeVar('PR', bound='PrivatePost')
A = TypeVar('A', bound='Admin')

class IncompletePost(BaseModel):
    """
    Неполный пост техникума, отправляется в списке.
    """
    id: int

    title: str
    """
    Заголовок поста.
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

    category: int

    @classmethod
    def from_database(cls: Type[IN], data: DatabasePost) -> IN:
        return IncompletePost(
            id = data.id,
            title = data.title,
            text = crop_first_paragraph(data.body),
            publish_date= round(float(data.publish_date.timestamp())),
            type=data.type,
            images=data.images.split("\n"),
            category=data.category
        )


class PublicPost(BaseModel):
    """
    Полный пост техникума
    """

    id: int

    title: str
    """
    Заголовок поста.
    """

    text: str
    """
    Текст поста.
    """

    publish_date: int
    """
    Timestamp создания
    """

    type: int
    author: str

    images: List[str]
    category: int

    @classmethod
    def from_database(cls: Type[PN], data: DatabasePost) -> PN:
        return PublicPost(
            id = data.id,
            images = data.images.split("\n"),
            title = data.title,
            text = data.body,
            publish_date= data.publish_date.timestamp(),
            type=data.type,
            author=data.author,
            category=data.category
        )

class PostablePost(BaseModel):
    """ Пост, который можно запостить """

    title: str = ""
    body: str = ""
    publish_date: int
    author: str = ""
    type: int
    status: PostStatus = PostStatus.Draft
    images: List[str]
    category: int

    def check(self):
        try:
            assert self.body != "", "Поле title обязательно"
            assert self.author != "", "Поле body обязательно"
            assert self.type >= 0, "Тип поста должен быть положительным"
            assert self.category >= 0, "Категория поста должен быть положительным"
            assert 0 <= self.status.value <= 1, "Статус поста должен быть в диапазоне 0-1"

            for file in self.images:
                assert os.path.isfile(f"database_files/{file}"), f"Файла с ID {file} нет"
        except AssertionError as error:
            raise HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=str(error)
            )

class PrivatePost(BaseModel):
    """ Пост + приватные данные """
    id: int
    title: str
    body: str
    publish_date: int
    images: List[str]
    author: str
    type: int
    status: PostStatus
    category: int

    @classmethod
    def from_database(cls: Type[PR], data: DatabasePost) -> PR:
        return PrivatePost(
            id = data.id,
            title = data.title,
            body = data.body,
            publish_date = round(float(data.publish_date.timestamp())),
            images = data.images.split("\n"),
            author = data.author,
            type = data.type,
            status = data.status,
            category=data.category
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

    @classmethod
    def from_database(cls: Type[A], data: DatabaseAdmin) -> A:
        return Admin(
            id=data.id,
            first_name=data.first_name,
            second_name=data.second_name,
            middle_name=data.middle_name
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
    Комментарий к посту
    """

    id: int

    post_id: int
    """
    ID Поста, к которой написан комментарий
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


class File(BaseModel):
    id: str
    name: str

    @classmethod
    def from_database(cls, data: DatabaseFile):
        return File(
            id = data.id,
            name = data.name
        )