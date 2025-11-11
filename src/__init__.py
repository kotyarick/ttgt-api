import os

os.makedirs("database/files", exist_ok=True)
os.makedirs("database/fixed_files", exist_ok=True)

from .database import FILES_PATH
from .routes.feedback import feedback_router
from .utils import regenerate_secret

if not os.path.isfile("secret"):
    regenerate_secret()

from fastapi.responses import Response, RedirectResponse

if not os.path.isdir(FILES_PATH):
    os.mkdir(FILES_PATH)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .routes.files import files_router
from .routes.admin import admin_router
from .routes.auth import auth_router
from .routes.content import content_router
from .routes.websocket import websocket_router
from .routes.schedule import schedule_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # FIXME: Перед отправкой на прод необходимо
        # раскомментировать эти ссылки,
        # чтобы можно было делать запросы
        # только с сайта ТТЖТ

        # "*://*.ttgt.org/*",
        # "*://ttgt.org/*",
        # "*://ttgt.org",
        # "*://*.ttgt.org",
        # "http://localhost:*",
        # "http://127.0.0.1:*",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", name="Основная страница")
async def index():
    """
    Редирект на /docs
    """
    return RedirectResponse("/docs")


@app.exception_handler(Exception)
async def exception_handler(
        request: Request,
        exc: Exception
):
    print(request.url, "Ошибка:", exc)
    return Response(
        status_code=500,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*"
        }
    )


app.include_router(websocket_router)
app.include_router(content_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(files_router)
app.include_router(feedback_router)
app.include_router(schedule_router)
