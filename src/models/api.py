import json
import mimetypes
import os.path
import re
from typing import Type, TypeVar, List, Optional

import fastapi
from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from starlette.status import HTTP_400_BAD_REQUEST

from ..database import Session, FILES_PATH
from ..models.database import DatabasePost, DatabaseTeacher, PostStatus, DatabaseAdmin, DatabaseFile, DatabaseVacancy, DatabaseSettings
from ..utils import crop_first_paragraph

IN = TypeVar('IN', bound='IncompletePost')
PN = TypeVar('PN', bound='PublicPost')
PR = TypeVar('PR', bound='PrivatePost')
A = TypeVar('A', bound='Admin')

def mime_of(name: str):
    return mimetypes.guess_type(name)[0] or "application/octet-stream"

class File(BaseModel):
    id: str
    name: str
    mime: str

    @classmethod
    def get_file(cls, id: str):
        if not id:
            return None
        if not os.path.isfile(f"{FILES_PATH}/{id}"):
            return None

        with Session.begin() as session:
            try:
                file = session.scalar(
                    select(DatabaseFile).where(DatabaseFile.id == id)
                )
            except:
                return None
            return File.from_database(file)

    @classmethod
    def get_files(cls, ids: List[str]):
        return list(filter(bool, [
            File.get_file(id)
            for id in ids
        ]))

    @classmethod
    def from_database(cls, data: DatabaseFile):
        return File(
            id=data.id,
            name=data.name,
            mime=mime_of(data.name)
        )

class IncompletePost(BaseModel):
    """
    Неполный пост техникума, отправляется в списке.
    """
    id: int

    title: str
    """
    Заголовок поста.
    """

    body: str
    """
    Первые несколько предложений.
    """

    publish_date: int
    """
    Timestamp создания
    """

    type: int

    files: List[File]

    category: int

    @classmethod
    def from_database(cls: Type[IN], data: DatabasePost) -> IN:
        return IncompletePost(
            id=data.id,
            title=data.title,
            body=crop_first_paragraph(data.body),
            publish_date=round(float(data.publish_date.timestamp())),
            type=data.type,
            files=File.get_files(data.files.split("\n")),
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

    body: str
    """
    Текст поста.
    """

    publish_date: int
    """
    Timestamp создания
    """

    type: int
    author: str

    files: List[File]
    category: int

    @classmethod
    def from_database(cls: Type[PN], data: DatabasePost) -> PN:
        return PublicPost(
            id=data.id,
            files=File.get_files(data.files.split("\n")),
            title=data.title,
            body=data.body,
            publish_date=data.publish_date.timestamp(),
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
    files: List[str]
    category: int

    def check(self):
        self.files = list(set(self.files))

        try:
            assert self.body != "", "Поле title обязательно"
            assert self.author != "", "Поле body обязательно"
            assert self.type >= 0, "Тип поста должен быть положительным"
            assert self.category >= 0, "Категория поста должен быть положительным"
            assert 0 <= self.status.value <= 1, "Статус поста должен быть в диапазоне 0-1"

            for file in self.files:
                assert os.path.isfile(f"{FILES_PATH}/{file}"), f"Файла с ID {file} нет"
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
    files: List[File]
    author: str
    type: int
    status: PostStatus
    category: int

    @classmethod
    def from_database(cls: Type[PR], data: DatabasePost) -> PR:
        return PrivatePost(
            id=data.id,
            title=data.title,
            body=data.body,
            publish_date=round(float(data.publish_date.timestamp())),
            files=File.get_files(data.files.split("\n")),
            author=data.author,
            type=data.type,
            status=data.status,
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


class LoginRequest(BaseModel):
    second_name: str
    password: str


class LoginResult(BaseModel):
    token: str
    admin: Admin


class CreateVacancy(BaseModel):
    title: str
    department: str
    salary: str
    is_active: bool
    created_at: int


class Vacancy(CreateVacancy):
    id: int

    @classmethod
    def from_database(cls, data: DatabaseVacancy):
        return Vacancy(
            id=data.id,
            title=data.title,
            department=data.department,
            salary=data.salary,
            is_active=data.is_active,
            created_at=data.created_at
        )

class Stats(BaseModel):
    online: int

class Event(BaseModel):
    updateStats: Optional[Stats] = None
    newPost: Optional[IncompletePost] = None
    removePost: Optional[int] = None
    updateFile: Optional[str] = None

    def encode(self):
        out = {}

        if self.updateStats:
            out["updateStats"] = self.updateStats.model_dump()

        if self.newPost:
            out["newPost"] = self.newPost.model_dump()

        if self.removePost:
            out["removePost"] = self.removePost

        if self.updateFile:
            out["updateFile"] = self.updateFile


        return out

class Feedback(BaseModel):
    """ Обращение граждан """


    first_name: str
    """ Имя """

    second_name: str
    """ Фамилия """

    middle_name: str
    """ Отчество """


    email: str
    """ Почта """

    phone: str
    """ Номер телефона """


    topic: str
    """ Тема сообщения """

    content: str
    """ Сообщение """


    def check(self):
        try:
            assert 0 < len(self.first_name) < 15,  "Имя не правильной длины"
            assert 0 < len(self.second_name) < 15, "Фамилия не правильной длины"
            assert     len(self.middle_name) < 15, "Отчество не правильной длины"

            assert re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email) is not None, "Почта не валидна"
            assert re.match(r"\+7[0-9]{10}", self.phone) is not None

            assert     len(self.topic) < 100,    "Тема слишком длинная"
            assert 0 < len(self.content) < 4096, "Сообщение слишком длинное"

        except AssertionError as error:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=error.args[0]
            )

class Settings(BaseModel):
    name: str
    value: dict
    enabled: bool

    def privatize(self):
        if self.enabled: return self

        self.value = None

        return self

    @classmethod
    def from_database(cls, data: DatabaseSettings):
        return Settings(
            name=data.name,
            value=json.loads(data.value),
            enabled=data.enabled
        )
