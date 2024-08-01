import os
from typing import Dict, List

from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from main.settings import BASE_DIR
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_USERNAME", ""),
    MAIL_PORT=587,
    MAIL_SERVER=os.getenv("MAIL_SERVER", ""),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=BASE_DIR / "templates",
)


fm = FastMail(conf)


async def send_email(
    recipeints: List[str],
    subject: str,
    context: Dict,
    template_name: str,
    background_task: BackgroundTasks,
):
    message = MessageSchema(
        subject=subject,
        recipients=recipeints,
        subtype=MessageType.html,
        template_body=context,
    )
    background_task.add_task(
        fm.send_message, message, template_name=template_name
    )
