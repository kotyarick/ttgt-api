from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi import status
from sqlalchemy import select

from api_tags import VACANCIES
from database import Session
from models.api import Vacancy, CreateVacancy
from models.database import DatabaseVacancy

vacancies_router = APIRouter(prefix="/vacancies", tags=[VACANCIES])


@vacancies_router.get("/", name="Получить список вакансий")
async def get_vacancies_list(
        offset: int = 0,
        limit: int = 20
) -> List[Vacancy]:
    limit = min(limit, 100)

    with Session.begin() as session:
        vacancies: List[DatabaseVacancy] = session.scalars(
            select(DatabaseVacancy).offset(offset).limit(limit)
        ).all()

        return [
            Vacancy.from_database(db_vacancy)
            for db_vacancy in vacancies
        ]


@vacancies_router.post("/", name="Добавить вакансию")
async def add_vacancy(
        vacancy: CreateVacancy
) -> Vacancy:
    with Session.begin() as session:
        dump = vacancy.model_dump()
        dump["created_at"] = datetime.fromtimestamp(dump["created_at"])
        db_vacancy = DatabaseVacancy(
            **dump
        )
        session.add(db_vacancy)
        session.flush()
        return Vacancy.from_database(db_vacancy)


@vacancies_router.delete(
    "/{vacancy_id:int}",
    name="Убрать вакансию",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_vacancy(
        vacancy_id: int
):
    with Session.begin() as session:
        session.query(DatabaseVacancy).filter(DatabaseVacancy.id == vacancy_id).delete()


@vacancies_router.patch("/{vacancy_id:int}", name="Отредактировать вакансию")
async def edit_vacancy(
        vacancy: CreateVacancy,
        vacancy_id: int
) -> Vacancy:
    with Session.begin() as session:
        if (
                session
                        .scalar(
                    select(DatabaseVacancy)
                            .where(DatabaseVacancy.id == vacancy_id)
                )
        ) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        dump = vacancy.model_dump()

        (
            session
            .query(DatabaseVacancy)
            .where(DatabaseVacancy.id == vacancy_id)
            .update(dump)
        )

        session.flush()
        return Vacancy.from_database(session.scalar(
            select(DatabaseVacancy).where(DatabaseVacancy.id == vacancy_id)
        ))
