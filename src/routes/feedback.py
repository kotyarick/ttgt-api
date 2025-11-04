from fastapi import APIRouter, HTTPException
from starlette import status
from starlette.status import HTTP_501_NOT_IMPLEMENTED

from src.database import Session
from src.models.api import Feedback
import smtplib
from email.message import EmailMessage

from src.utils import config

feedback_router = APIRouter(
    prefix="/feedback",
    tags=[]
)

@feedback_router.post("/", status_code=status.HTTP_204_NO_CONTENT)
async def create_feedback(
        feedback: Feedback
):
    feedback.check()
    email = config["email"]

    if email["password"] == "":
        raise HTTPException(
            status_code=HTTP_501_NOT_IMPLEMENTED,
            detail="Пароля на сервере нету, поэтому письмо не отправится"
        )

    msg = EmailMessage()
    msg['Subject'] = feedback.topic or "Новое обращение"
    msg['From'] = email["email"]
    msg['To'] = email["forward_to"]
    msg.set_content(f"""Обращение от {feedback.second_name} {feedback.first_name} {feedback.middle_name}
Email: {feedback.email}
Телефон: {feedback.phone}

Обращение:
{feedback.content}
""")

    with smtplib.SMTP(email["server"], 587) as server:
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.login(email["email"], email["password"])  # Log in to your email account
        server.send_message(msg)  # Send the email

        msg = EmailMessage()
        msg['Subject'] = "Мы вас услышали"
        msg['From'] = email["email"]
        msg['To'] = feedback.email
        msg.set_content(f"""{feedback.second_name}, ваша заявка принята. Ожидайте ответа.

Текст заявки:
{feedback.content}""")

