import random
import string
from sys import argv

from argon2 import PasswordHasher

from database import Session
from models.database import DatabaseTeacher
from utils import regenerate_secret

if len(argv) < 2:
    argv.append("")

match argv[1]:
    case "create-account":
        print("Добавление аккаунта админа.")
        first_name = input("Имя: ")
        second_name = input("Фамилия: ")
        middle_name = input("Отчество (можно оставить пустым): ")
        password = input("Пароль (если оставить пустым, то будет сгенерирован и написан случайный пароль): ")
        if not password:
            for _ in range(15):
                password += random.choice(string.ascii_letters + string.digits)
            print("Пароль:", password)

        hasher = PasswordHasher()
        password_hash = hasher.hash(password)

        with Session.begin() as session:
            session.add(
                DatabaseTeacher(
                    first_name = first_name,
                    second_name = second_name,
                    middle_name = middle_name,
                    password_hash = password_hash
                )
            )
        print("Аккаунт админа добавлен.")
    case "regenerate-secret":
        if input("""Вы уверены, что хотите пересоздать секрет? Это приведёт к выходу из системы всех администраторов.
Напишите ДА для подтверждения или любое другое слово для отмены.  """).lower().strip() != "да":
            print("Действие отменено.")
            exit(0)

        regenerate_secret()
        print("Секрет изменён, всем администраторам придётся входить заново.")
    case default:
        print("""Средства системного администратора
create-account - создать новый аккаунт администратора
regenerate-secret - Сгенерировать новый секрет""")
