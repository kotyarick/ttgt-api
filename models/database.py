import enum
from typing import Optional

from sqlalchemy import String, ForeignKey, Boolean, Column, DateTime, func, Enum
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.orm.attributes import Mapped


class PostStatus(enum.Enum):
    """
    Статус поста
    """

    Draft = 0
    """ Черновик. Не отображается на главной странице """

    Published = 1
    """ Пост опубликован """


class Base(DeclarativeBase):
    pass


class DatabasePost(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str]
    body: Mapped[str]
    publish_date = Column(DateTime(timezone=True), server_default=func.now())
    files: Mapped[str]
    author: Mapped[str] = mapped_column(String(100))
    type: Mapped[int]
    status = Column(Enum(PostStatus))
    category: Mapped[int]


class DatabaseVacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)

    title = Column(String(255))
    department = Column(String(255))
    salary = Column(String(100))
    is_active = Column(Boolean())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DatabaseSettings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True)

    key = String(100)
    value = String()


class DatabaseAdmin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)

    first_name: Mapped[str]
    """ Имя """

    second_name: Mapped[str]
    """ Фамилия """

    middle_name: Mapped[Optional[str]]
    """ Отчество """

    password_hash: Mapped[str]


class DatabaseTeacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)

    initials: Mapped[str]
    """ Инициалы """


class DatabaseComment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id = mapped_column(ForeignKey("posts.id"))
    sender_name = Column(String(16), nullable=False)
    sender_email = Column(String(64), nullable=False)
    content = Column(String(512), nullable=False)
    approved = Column(Boolean(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DatabaseAppeal(Base):
    __tablename__ = "appeals"

    id: Mapped[int] = mapped_column(primary_key=True)
    email = Column(String(64), nullable=False)
    phone = Column(String(12), nullable=False)
    message = Column(String(512), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DatabaseFile(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = Column(String(), nullable=False)
    deattached: Mapped[bool] = Column(Boolean(), nullable=False)