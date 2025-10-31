from typing import Annotated, TypeAlias

from fastapi import Depends, APIRouter, Header
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from api_tags import ADMIN_ONLY
from models.api import Admin
from routes.auth import extract_jwt
from .vacancies import vacancies_router
from ..websocket import broadcast_event
from ...models.api import Event


def admin_login(
        x_authorization: Annotated[str, Header()],
) -> Admin:
    return extract_jwt(x_authorization)


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


@admin_router.patch("/{fixed_file:str}")
async def update_file(
        fixed_file: str,
        request: Request
):
    fixed_files = {
        "zamena": "zamena.pdf"
    }

    if not fixed_file in fixed_files:
        return None

    file_name = fixed_files[fixed_file]

    with open(f"database/fixed_files/{file_name}", "wb") as f:
        f.write(await request.body())

    await broadcast_event(Event(
        updateFile=fixed_file
    ))

    return { }