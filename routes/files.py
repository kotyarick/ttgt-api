import os.path
from hashlib import sha256
from io import BytesIO

import magic
from PIL import Image
from fastapi import APIRouter, Request, HTTPException
from fastapi import status
from sqlalchemy import select
from fastapi.responses import FileResponse

from api_tags import FILES, ADMIN_ONLY
from database import Session
from models.api import File
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
        filename: str
):
    """
    Выложить файл. На выходе даёт ID. ID файла - это sha256
    """
    body = await request.body()
    #with open("/tmp/file", "wb") as f:
    #    f.write(body)

    is_image = magic.Magic(mime=True).from_buffer(body).startswith("image/")

    if is_image:
        img = Image.open(BytesIO(body))

        # Create output buffer
        output_buffer = BytesIO()

        # Save compressed image to buffer
        img.save(output_buffer, format="png", quality=0.7, optimize=True)

        # Get buffer bytes
        output_buffer.seek(0)
        body = output_buffer.read()

    file_hash = sha256(body).hexdigest()

    if os.path.exists(f"database_files/{file_hash}"):
        return {"id": file_hash}

    with open(f"database_files/{file_hash}", "wb") as file:
        file.write(body)

    with Session.begin() as session:
        session.add(DatabaseFile(
            id=file_hash,
            name=filename
        ))

    return { "id": file_hash }

@files_router.get(
    "/{file_id:str}",
    name="Скачать файл"
)
async def get_file(
        file_id: str
):
    """
    После ID файла можно указать расширение
    """
    file_id = file_id.split(".", 1)[0]
    if not os.path.isfile(f"database_files/{file_id}"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    with Session.begin() as session:
        db_file = session.scalar(
            select(DatabaseFile)
                .where(DatabaseFile.id == file_id)
        )

        if not db_file:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        file = File.from_database(db_file)

    mime = magic.Magic(mime=True).from_buffer(open(f"database_files/{file_id}", "rb").read())

    return FileResponse(
        f"database_files/{file_id}",
        headers={
            'Content-Disposition': f'attachment; filename="{file.name}',
            "content-type": mime
        }
    )