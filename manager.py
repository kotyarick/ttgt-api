import os.path
import random
import string
from sys import argv

from argon2 import PasswordHasher

from database import Session
from models.database import DatabaseTeacher, DatabaseAdmin
from utils import regenerate_secret

if len(argv) < 2:
    argv.append("")


def non_empty(user_input: str) -> bool:
    """
    Для использования в `checked_input`

    Проверяет пуста ли строка.
    Строка исключительно из пробелов считается пустой.
    """
    return user_input.strip() != ""


def checked_input(prompt: str, check) -> str:
    """
    Запрашивает ввод повторно до тех пор,
    пока ввод не будет удовлетворять условию.
    """

    while True:
        user_intput = input(prompt)
        if check(user_intput):
            return user_intput


match argv[1]:
    case "create-account":
        print("Добавление аккаунта админа.")
        first_name = checked_input("Имя: ", non_empty)
        second_name = checked_input("Фамилия: ", non_empty)
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
                DatabaseAdmin(
                    first_name=first_name,
                    second_name=second_name,
                    middle_name=middle_name,
                    password_hash=password_hash
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
    case "add-teachers":
        if not os.path.isfile("teachers.txt"):
            print("Создайте файл teachers.txt, добавьте туда учителей на отдельные строки")

        with Session.begin() as session:
            for teacher in open("teachers.txt").readlines():
                if not teacher: continue
                session.add(DatabaseTeacher(initials=teacher.strip()))
    case default:
        print("""Средства системного администратора
create-account - создать новый аккаунт администратора
regenerate-secret - Сгенерировать новый секрет
add-teachers - Добавить учителей из файла""")
