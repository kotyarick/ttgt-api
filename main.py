import os
from utils import regenerate_secret

if not os.path.isfile("secret"):
    regenerate_secret()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.admin import adminRouter
from routes.auth import authRouter
from routes.content import contentRoutes



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
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

app.include_router(contentRoutes)
app.include_router(authRouter)
app.include_router(adminRouter)