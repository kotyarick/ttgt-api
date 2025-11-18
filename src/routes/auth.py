import json
from base64 import b64encode, b64decode
from datetime import datetime
from hashlib import sha256
from typing import Optional

from argon2 import PasswordHasher
from fastapi import APIRouter, HTTPException
from fastapi import status
from sqlalchemy import select

from ..api_tags import ADMIN_ONLY
from ..database import Session
from ..models.api import LoginRequest, LoginResult, Admin
from ..models.database import DatabaseAdmin

auth_router = APIRouter(prefix="/auth")

secret = open("secret", "rb").read()
hasher = PasswordHasher()


def create_jwt(user: Admin) -> str:
    """ Создаёт JWT токен из данных админа """

    jwt = b64encode(
        #  Данные о токене
        json.dumps({
            #  Истекает через полгода
            "expires_at": datetime.now().timestamp() + 15552000
        }).encode()
        #  Данные о пользователе
    ).decode() + "." + b64encode(
        user.model_dump_json().encode()
    ).decode()

    #  Подпись
    jwt += "." + sha256((secret + jwt.encode())).hexdigest()

    return jwt


def extract_jwt(jwt: str,  expect_type: Optional[int] = None) -> Admin:
    """Получает данные из JWT токена

    В случае ошибки создаёт HTTPException
    """
    try:
        #  Поверяем, что токен не None
        #  и не пустая строка
        assert jwt, "JWT отсутствует"

        metadata, admin_data, signature = jwt.encode().split(b".")

        #  1. Проверяем подпись
        assert signature.decode() == sha256(
            secret + metadata + b"." + admin_data).hexdigest(), "Подпись не действительна"

        #  2. Достаём данные
        metadata, admin_data = (json.loads(b64decode(metadata).decode()),
                                json.loads(b64decode(admin_data).decode()))

        #  3. Проверяем тип админа, если указан
        assert expect_type is None or admin_data.get("type") == expect_type, "Не верный тип админа"

        #  4. Проверяем протух ли токен
        assert metadata["expires_at"] > datetime.now().timestamp(), "Токен истёк"

        #  5. Даём данные из токена
        return Admin(**admin_data)
    except Exception as exception:
        print("Не удалось достать JWT:", exception)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@auth_router.post("/login", name="Войти в систему", tags=[ADMIN_ONLY])
async def login(request: LoginRequest) -> LoginResult:
    """ Получить токен
    
    Вместо логина необходимо использовать свою фамилию
    При не верном логине или пароле можно получить 401
    """
    try:
        with (Session.begin() as session):
            db_admin: DatabaseAdmin = session.scalar(
                select(DatabaseAdmin)
                .where(DatabaseAdmin.second_name == request.second_name)
            )

            hasher.verify(db_admin.password_hash, request.password)

            admin = Admin.from_database(db_admin)

        return LoginResult(
            token=create_jwt(admin),
            admin=admin
        )
    except Exception as exception:
        print("Ошибка входа:", exception)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
