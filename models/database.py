import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey, Boolean, Column, DateTime, func, Enum, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.api import Teacher


class NewsType(enum.Enum):
    News = 0
    Achievement = 1
    Education = 2
    Event = 3



class NewsStatus(enum.Enum):
    Draft = 0
    Published = 1

class Base(DeclarativeBase):
     pass

class DatabaseNews(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)

    slug = Column(String(15), unique=True, nullable=False)
    title: Mapped[str]
    body: Mapped[str]
    publish_date = Column(DateTime(timezone=True), server_default=func.now())
    image_amount: Mapped[int]
    author: Mapped[str] = mapped_column(String(100))
    type = Column(Enum(NewsType))
    status = Column(Enum(NewsStatus))

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

    first_name: Mapped[str]
    """ Имя """

    second_name: Mapped[str]
    """ Фамилия """

    middle_name: Mapped[Optional[str]]
    """ Отчество """

    @classmethod
    def from_database(cls, data: Teacher):
        return Teacher(
            id = data.id,
            first_name = data.first_name,
            second_name = data.second_name,
            middle_name = data.middle_name
        )

class DatabaseComment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    news_id = mapped_column(ForeignKey("news.id"))
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