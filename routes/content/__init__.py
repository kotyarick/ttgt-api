from fastapi import APIRouter

from .news import newsRouter

contentRouter = APIRouter(prefix="/content")

contentRouter.include_router(newsRouter)
