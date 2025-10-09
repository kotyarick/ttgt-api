from typing import Annotated, TypeAlias

from fastapi import Depends, APIRouter, Header

from models.api import Admin
from routes.auth import extract_jwt


def admin_login(
        x_authorization: Annotated[str | None, Header()] = None,
) -> Admin:
    return extract_jwt(x_authorization)

AdminRequired: TypeAlias = Annotated["Admin", Depends(admin_login)]

adminRouter = APIRouter(prefix="/admin")

@adminRouter.get("/super-secret")
async def get_super_secret_data(
        admin: AdminRequired
) -> dict[str, str]:
    print(admin)
    return { "data": "У тебя получилось" }

from .news import newsRouter
from .teachers import teachersRouter

adminRouter.include_router(newsRouter)
adminRouter.include_router(teachersRouter)