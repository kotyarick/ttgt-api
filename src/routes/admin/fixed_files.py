from collections.abc import Callable
from typing import Optional, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.requests import Request
from pydantic.v1 import BaseModel
from starlette.status import HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED

from src.api_tags import ADMIN_ONLY, FILES
from src.models.api import Event, AdminType
from src.routes.admin import admin_login, AdminRequired, siteAdminDependency
from src.routes.websocket import broadcast_event
from src.routes.schedule.schedule_parser import update

fixed_files_router = APIRouter(
    prefix="/fixedfiles",
    tags=[FILES],
    dependencies=[siteAdminDependency]
)

class FixedFile(BaseModel):
    name: str
    post_update: Optional[Callable[[], None]] = None
    admin_type: int = AdminType.Site

fixed_files: Dict[str, FixedFile] = {
    "zamena": FixedFile(
        name="zamena.pdf"
    ),
    "schedule": FixedFile(
        name="schedule.zip",
        post_update=lambda: update(True),
        admin_type=AdminType.Schedule
    )
}

@fixed_files_router.patch(
    "/{fixed_file:str}",
    status_code=HTTP_204_NO_CONTENT,
    name="Отправить фиксированный файл"
)
async def update_file(
        fixed_file: str,
        request: Request,
        admin: AdminRequired
):
    if not fixed_file in fixed_files:
        return None

    file = fixed_files[fixed_file]

    if file.admin_type != admin.type:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    with open(f"database/fixed_files/{file.name}", "wb") as f:
        f.write(await request.body())

    if file.post_update:
        file.post_update()
    
    await broadcast_event(Event(
        updateFile=fixed_file
    ))

    return None
