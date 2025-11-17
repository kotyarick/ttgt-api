import os.path
import traceback
from hashlib import sha256
from io import BytesIO
from typing import Optional

from PIL import Image
from fastapi import APIRouter, Request, HTTPException, UploadFile
from fastapi import status
from fastapi.responses import FileResponse
from sqlalchemy import select

from .admin.fixed_files import fixed_files
from ..api_tags import FILES, ADMIN_ONLY
from ..database import Session, FILES_PATH
from ..models.api import File, mime_of
from ..models.database import DatabaseFile
from ..routes.admin import AdminRequired

files_router = APIRouter(
    prefix="/files",
    tags=[FILES]
)


@files_router.get(
    "/fixed/{fixed_file:str}",
    name="Скачать фиксированный файл"
)
async def get_fixed_file(fixed_file: str):
    if not fixed_file in fixed_files:
        return None

    file_name = fixed_files[fixed_file]
    path = f"database/fixed_files/{file_name}"

    return FileResponse(
        path,
        media_type=mime_of(path),
        content_disposition_type="inline"
    )

@files_router.post(
    "/", tags=[ADMIN_ONLY],
    name="Добавить файл"
)
async def upload(
        file: UploadFile,
        _admin: AdminRequired,
):
    """
    Выложить файл. На выходе даёт ID. ID файла - это sha256
    """
    # with open("/tmp/file", "wb") as f:
    #    f.write(body)

    filename = file.filename
    file = file.file.read()

    is_image = mime_of(filename)

    if is_image:
        try:
            img = Image.open(BytesIO(file))

            # Create output buffer
            output_buffer = BytesIO()

            # Save compressed image to buffer
            img.save(output_buffer, format="png", quality=0.7, optimize=True)

            # Get buffer bytes
            output_buffer.seek(0)
            file = output_buffer.read()
        except:
            traceback.format_exc()

    file_hash = sha256(file).hexdigest()

    if os.path.exists(f"{FILES_PATH}/{file_hash}"):
        return { "id": file_hash }

    with open(f"{FILES_PATH}/{file_hash}", "wb") as f:
        f.write(file)

    with Session.begin() as session:
        if session.scalar(
            select(DatabaseFile.id).where(DatabaseFile.id == file_hash)
        ):
            return { "id": file_hash }

        session.add(DatabaseFile(
            id=file_hash,
            name=filename,
        ))

    return { "id": file_hash }


@files_router.get(
    "/{file_name:str}",
    name="Скачать файл"
)
async def get_file(file_name: str):
    """
    После ID файла можно указать расширение
    """
    file_id = file_name.split(".", 1)[0]

    with Session.begin() as session:
        db_file = session.scalar(
            select(DatabaseFile)
            .where(DatabaseFile.id == file_id)
        ) or session.scalar(
            select(DatabaseFile)
            .where(DatabaseFile.name == file_name)
        )

        if not db_file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        file = File.from_database(db_file)

    return FileResponse(
        f"{FILES_PATH}/{file.id}",
        filename=file.name,
        media_type=file.mime,
        content_disposition_type="inline"
    )
