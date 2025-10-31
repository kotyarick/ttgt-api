from fastapi import APIRouter

from ...api_tags import CONTENT
from .posts import posts_router
from .vacancies import vacancies_router

content_router = APIRouter(
    prefix="/content",
    tags=[CONTENT]
)

content_router.include_router(posts_router)
content_router.include_router(vacancies_router)
