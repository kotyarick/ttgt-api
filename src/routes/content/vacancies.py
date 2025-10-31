from typing import List

from fastapi import APIRouter
from sqlalchemy import select

from api_tags import VACANCIES
from database import Session
from models.api import Vacancy
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
            select(DatabaseVacancy).offset(offset).limit(limit).where(DatabaseVacancy.is_active == True)
        ).all()

        return [
            Vacancy.from_database(db_vacancy)
            for db_vacancy in vacancies
        ]