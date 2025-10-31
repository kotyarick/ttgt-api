import mimetypes
import os.path
from typing import Type, TypeVar, List, Optional

import fastapi
from fastapi import HTTPException
from magic import Magic
from pydantic import BaseModel
from sqlalchemy import select

from database import Session
from models.database import DatabasePost, DatabaseTeacher, PostStatus, DatabaseAdmin, DatabaseFile, DatabaseVacancy
from utils import crop_first_paragraph

IN = TypeVar('IN', bound='IncompletePost')
PN = TypeVar('PN', bound='PublicPost')
PR = TypeVar('PR', bound='PrivatePost')
A = TypeVar('A', bound='Admin')

def mime_of(name: str, id: str = None, buf = None):
    mime = Magic(mime=True).from_buffer(buf or open(f"database_files/{id}", "rb").read())

    if mime == "application/octet-stream":
        mime = mimetypes.guess_type(name)[0] or "application/octet-stream"

    return mime

class File(BaseModel):
    id: str
    name: str
    mime: str

    @classmethod
    def get_file(cls, id: str):
        if not id:
            return None
        if not os.path.isfile(f"database_files/{id}"):
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
            mime=mime_of(data.name, data.id)
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
        try:
            assert self.body != "", "Поле title обязательно"
            assert self.author != "", "Поле body обязательно"
            assert self.type >= 0, "Тип поста должен быть положительным"
            assert self.category >= 0, "Категория поста должен быть положительным"
            assert 0 <= self.status.value <= 1, "Статус поста должен быть в диапазоне 0-1"

            for file in self.files:
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
            created_at=round(float(data.created_at.timestamp()))
        )

class Stats(BaseModel):
    online: int

class Event(BaseModel):
    updateStats: Optional[Stats] = None
    newPost: Optional[IncompletePost] = None
    removePost: Optional[int] = None

    def encode(self):
        out = {}

        if self.updateStats:
            out["updateStats"] = self.updateStats.model_dump()

        if self.newPost:
            out["newPost"] = self.newPost.model_dump()

        if self.removePost:
            out["removePost"] = self.removePost

        return out