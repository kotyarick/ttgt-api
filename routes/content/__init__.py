from fastapi import APIRouter

from api_tags import CONTENT
from .news import newsRouter

contentRouter = APIRouter(
    prefix="/content",
    tags=[CONTENT]
)

contentRouter.include_router(newsRouter)
