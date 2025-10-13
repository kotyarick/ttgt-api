import os

from fastapi.responses import Response

from routes.files import filesRouter
from utils import regenerate_secret

if not os.path.isfile("secret"):
    regenerate_secret()

if not os.path.isdir("database_files"):
    os.mkdir("database_files")

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from routes.admin import adminRouter
from routes.auth import authRouter
from routes.content import contentRouter



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        #FIXME: Перед отправкой на прод необходимо
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

app.include_router(contentRouter)
app.include_router(authRouter)
app.include_router(adminRouter)
app.include_router(filesRouter)