import mimetypes
import os.path
import traceback
from hashlib import sha256
from io import BytesIO
from typing import Optional

import magic
from PIL import Image
from fastapi import APIRouter, Request, HTTPException
from fastapi import status
from fastapi.responses import FileResponse
from sqlalchemy import select

from api_tags import FILES, ADMIN_ONLY
from database import Session, FILES_PATH
from models.api import File, mime_of
from models.database import DatabaseFile
from routes.admin import AdminRequired

files_router = APIRouter(
    prefix="/files",
    tags=[FILES]
)

@files_router.post(
    "/", tags=[ADMIN_ONLY],
    name="Добавить файл"
)
async def upload(
        request: Request,
        _admin: AdminRequired,
        filename: str,
        deattached: Optional[str]
):
    """
    Выложить файл. На выходе даёт ID. ID файла - это sha256
    """
    body = await request.body()
    # with open("/tmp/file", "wb") as f:
    #    f.write(body)

    is_image = mime_of(filename, buf=body)

    if is_image:
        try:
            img = Image.open(BytesIO(body))

            # Create output buffer
            output_buffer = BytesIO()

            # Save compressed image to buffer
            img.save(output_buffer, format="png", quality=0.7, optimize=True)

            # Get buffer bytes
            output_buffer.seek(0)
            body = output_buffer.read()
        except:
            traceback.format_exc()

    file_hash = sha256(body).hexdigest()

    if os.path.exists(f"{FILES_PATH}/{file_hash}"):
        return { "id": file_hash }

    with open(f"{FILES_PATH}/{file_hash}", "wb") as file:
        file.write(body)

    with Session.begin() as session:
        if session.scalar(
            select(DatabaseFile.id).where(DatabaseFile.id == file_hash)
        ):
            return { "id": file_hash }

        session.add(DatabaseFile(
            id=file_hash,
            name=filename,
            deattached=deattached is not None
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
