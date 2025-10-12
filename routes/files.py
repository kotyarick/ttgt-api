from fastapi import APIRouter, Request


filesRouter = APIRouter(
    prefix="/files"
)

async def upload(
        request: Request,

):
    ...