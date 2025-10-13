from typing import Annotated, TypeAlias

from fastapi import Depends, APIRouter, Header

from api_tags import ADMIN_ONLY
from models.api import Admin
from routes.auth import extract_jwt


def admin_login(
        x_authorization: Annotated[str, Header()],
) -> Admin:
    return extract_jwt(x_authorization)

#  Depends, который даёт информацию об админе
#  из токена в заголовке запроса
#  или даёт 401 при ошибке
AdminRequired: TypeAlias = Annotated["Admin", Depends(admin_login)]

admin_router = APIRouter(prefix="/admin", tags=[ADMIN_ONLY])

@admin_router.get("/super-secret")
async def get_super_secret_data(
        admin: AdminRequired
) -> dict[str, str]:
    print(admin)
    return { "data": "У тебя получилось" }

from .posts import posts_router
from .teachers import teachers_router

admin_router.include_router(posts_router)
admin_router.include_router(teachers_router)
