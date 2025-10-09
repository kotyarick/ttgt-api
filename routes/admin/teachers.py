from typing import List

from fastapi import APIRouter
from sqlalchemy import select
from fastapi import status

from database import Session
from models.api import Teacher, CreateTeacher
from models.database import DatabaseTeacher
from routes.admin import AdminRequired

teachersRouter = APIRouter(prefix="/teachers")

@teachersRouter.get("/", name="Получить список преподавателей")
async def get_teachers_list(
        admin: AdminRequired,
        offset: int = 0,
        limit: int = 20
) -> List[Teacher]:
    limit = min(limit, 20)

    with Session.begin() as session:
        teachers: List[Teacher] = session.scalars(
            select(Teacher).offset(offset).limit(limit)
        ).all()

        return [
            Teacher.from_database(db_teacher)
            for db_teacher in teachers
        ]

@teachersRouter.post("/", name="Добавить преподавателя")
async def add_teacher(
        admin: AdminRequired,
        teacher: CreateTeacher
) -> Teacher:
    with Session.begin() as session:
        db_teacher = DatabaseTeacher(
            **teacher.model_dump()
        )
        session.add(db_teacher)
        session.flush()
        return Teacher.from_database(db_teacher)

@teachersRouter.delete(
    "/{teacher_id:int}",
    name="Убрать преподавателя",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_teacher(
        admin: AdminRequired,
        teacher_id: int
):
    with Session.begin() as session:
        session.query(DatabaseTeacher).filter(DatabaseTeacher.id == teacher_id).delete()

