from fastapi import APIRouter, HTTPException

from .news import newsRouter


contentRouter = APIRouter(prefix="/content")

contentRouter.include_router(newsRouter)
