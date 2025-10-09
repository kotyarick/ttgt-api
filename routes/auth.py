import json
from base64 import b64encode, b64decode
from hashlib import sha256
from typing import Annotated

from argon2 import PasswordHasher
from fastapi import APIRouter, HTTPException, Header, Depends
from datetime import datetime

from fastapi import status
from sqlalchemy import select

from database import Session
from models.api import LoginRequest, LoginResult, Admin
from models.database import DatabaseAdmin

authRouter = APIRouter(prefix="/auth")

secret = open("secret", "rb").read()
hasher = PasswordHasher()

def create_jwt(user: Admin) -> str:
    jwt = b64encode(
        json.dumps({
            # Истекает через месяц
            "expires_at": datetime.now().timestamp() + 2592000
        }).encode()
    ).decode()+"."+b64encode(
        user.model_dump_json().encode()
    ).decode()

    jwt += "." + sha256((secret + jwt.encode())).hexdigest()

    return jwt

def extract_jwt(jwt: str) -> Admin:
    try:
        metadata, admin_data, signature = jwt.encode().split(b".")

        #  1. Проверяем подпись
        assert signature.decode() == sha256(secret + metadata + b"." + admin_data).hexdigest()

        #  2. Достаём данные
        metadata, admin_data = (json.loads(b64decode(metadata).decode()),
                                json.loads(b64decode(admin_data).decode()))
        #  3. Проверяем протух ли токен
        assert metadata["expires_at"] > datetime.now().timestamp()

        #  4. Даём данные из токена
        return Admin(**admin_data)
    except Exception as exception:
        print("Extract JWT error: ", exception)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@authRouter.post("/login")
async def login(request: LoginRequest) -> LoginResult:
    try:
        with (Session.begin() as session):
            db_admin: DatabaseAdmin = session.scalar(
                select(DatabaseAdmin)
                    .where(
                        DatabaseAdmin.second_name ==
                        request.second_name
                    )
            )

            hasher.verify(db_admin.password_hash, request.password)

            admin = Admin.from_database(db_admin)

        return LoginResult(
            token=create_jwt(admin),
            admin=admin
        )
    except Exception as exception:
        print("Login error:", exception)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

def admin_login(
        x_authorization: Annotated[str | None, Header()] = None,
) -> Admin:
    return extract_jwt(x_authorization)