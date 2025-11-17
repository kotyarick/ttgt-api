from typing import Annotated, TypeAlias

from fastapi import Depends, APIRouter, Header

from ...api_tags import ADMIN_ONLY
from ...models.api import Admin
from ...routes.auth import extract_jwt
from .vacancies import vacancies_router
from .settings import admin_settings_router


def admin_login(
        x_authorization: Annotated[str, Header()],
) -> Admin:
    return extract_jwt(x_authorization)

from .fixed_files import fixed_files_router

#  Depends, который даёт информацию об админе
#  из токена в заголовке запроса
#  или даёт 401 при ошибке
AdminRequired: TypeAlias = Annotated["Admin", Depends(admin_login)]

admin_router = APIRouter(prefix="/admin", tags=[ADMIN_ONLY], dependencies=[Depends(admin_login)])

from .posts import posts_router
from .teachers import teachers_router

admin_router.include_router(posts_router)
admin_router.include_router(teachers_router)
admin_router.include_router(vacancies_router)
admin_router.include_router(fixed_files_router)
admin_router.include_router(admin_settings_router)
