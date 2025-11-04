from fastapi import APIRouter, Depends
from fastapi.requests import Request
from starlette.status import HTTP_204_NO_CONTENT

from src.api_tags import ADMIN_ONLY, FILES
from src.models.api import Event
from src.routes.admin import admin_login
from src.routes.websocket import broadcast_event

fixed_files_router = APIRouter(
    prefix="/fixedfiles",
    tags=[ADMIN_ONLY, FILES],
    dependencies=[Depends(admin_login)]
)

fixed_files = {
    "zamena": "zamena.pdf"
}

@fixed_files_router.patch("/{fixed_file:str}", status_code=HTTP_204_NO_CONTENT)
async def update_file(
        fixed_file: str,
        request: Request
):
    if not fixed_file in fixed_files:
        return None

    file_name = fixed_files[fixed_file]

    with open(f"database/fixed_files/{file_name}", "wb") as f:
        f.write(await request.body())

    await broadcast_event(Event(
        updateFile=fixed_file
    ))

