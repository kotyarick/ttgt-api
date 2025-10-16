from typing import List

from fastapi import APIRouter
from fastapi import status
from sqlalchemy import select

from api_tags import TEACHERS
from database import Session
from models.api import Teacher, CreateTeacher
from models.database import DatabaseTeacher
from routes.admin import AdminRequired

teachers_router = APIRouter(prefix="/teachers", tags=[TEACHERS])


@teachers_router.get("/", name="Получить список преподавателей")
async def get_teachers_list(
        offset: int = 0,
        limit: int = 20
) -> List[Teacher]:
    limit = min(limit, 100)

    with Session.begin() as session:
        teachers: List[DatabaseTeacher] = session.scalars(
            select(DatabaseTeacher).offset(offset).limit(limit)
        ).all()

        return [
            Teacher.from_database(db_teacher)
            for db_teacher in teachers
        ]


@teachers_router.post("/", name="Добавить преподавателя")
async def add_teacher(
        teacher: CreateTeacher
) -> Teacher:
    with Session.begin() as session:
        db_teacher = DatabaseTeacher(
            **teacher.model_dump()
        )
        session.add(db_teacher)
        session.flush()
        return Teacher.from_database(db_teacher)


@teachers_router.delete(
    "/{teacher_id:int}",
    name="Убрать преподавателя",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_teacher(
        teacher_id: int
):
    with Session.begin() as session:
        session.query(DatabaseTeacher).filter(DatabaseTeacher.id == teacher_id).delete()
