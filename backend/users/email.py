import os
from typing import Dict, List

from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from main import settings
from main.settings import BASE_DIR
from pydantic import BaseModel, EmailStr
from cryptography.fernet import Fernet
from starlette.responses import JSONResponse


conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_USERNAME", ""),
    MAIL_PORT=587,
    MAIL_SERVER=os.getenv("MAIL_SERVER", ""),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER=BASE_DIR / "templates",
)


fm = FastMail(conf)


async def send_email(
    recipients: List[str],
    subject: str,
    context: Dict,
    template_name: str,
    background_task: BackgroundTasks,
):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        subtype=MessageType.html,
        template_body=context,
    )
    background_task.add_task(
        fm.send_message, message, template_name=template_name
    )


async def send_account_verification_email(
    obj, background_tasks: BackgroundTasks, context: str
):
    """
    send both user and theatre verification emaail
    """
    from .auth import hash_password
    from main import settings
    string_context = obj.get_context_string(context=context)
    cy_key = Fernet(settings.KEY.encode())
    token = cy_key.encrypt(string_context).decode()
    email = cy_key.encrypt(obj.email.encode()).decode()
    activate_url = f"{settings.HOST_APP}/auth/account-verify?token={token}&p={email}"
    data = {"app_name": "Movy", "name": obj.get_name, "verification_link": activate_url}
    subject = f"Account Verification Movy APP"
    template_name = "user/account-verification.html"
    await send_email(
        recipients=[obj.email],
        subject=subject,
        context=data,
        template_name=template_name,
        background_task=background_tasks,
    )
