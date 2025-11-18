from fastapi import APIRouter

from ...api_tags import COURSES

courses_router = APIRouter(
    prefix="/courses",
    tags=[COURSES]
)

