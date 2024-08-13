import os
from typing import Dict, List

from cryptography.fernet import Fernet
from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from main import settings
from main.settings import BASE_DIR
from .utils import _encode_token

from .auth import hash_password

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_USERNAME", ""),
    MAIL_PORT=465,
    MAIL_SERVER=os.getenv("MAIL_SERVER", ""),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
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
    from main import settings

    print(obj, 'obj.............')
    string_context = obj.get_context_string(context=context)
    token = _encode_token(string_context)
    email = _encode_token(obj.email.encode())
    activate_url = (
        f"{settings.HOST_APP}/auth/account-verify?token={token}&id={email}"
    )
    current_year = obj.created_at.year
    data = {
        "app_name": "Movy",
        "name": obj.get_name,
        "verification_link": activate_url,
        "current_year": current_year,
    }
    subject = "Movy Account Verification"
    template_name = "user/account-verification.html"
    await send_email(
        recipients=[obj.email],
        subject=subject,
        context=data,
        template_name=template_name,
        background_task=background_tasks,
    )


async def send_account_activation_email(
    obj, background_tasks: BackgroundTasks
):
    """
    send both user and theatre activation email
    """
    current_year = obj.created_at.year
    data = {
        "app_name": "Movy",
        "name": obj.get_name,
        "current_year": current_year,
    }
    subject = "Movy Account Activation"
    template_name = "user/account-activation.html"
    await send_email(
        recipients=[obj.email],
        subject=subject,
        context=data,
        template_name=template_name,
        background_task=background_tasks,
    )


async def reset_password_email(
    obj, background_tasks: BackgroundTasks, context: str
):
    """
    send both user and theatre verification emaail
    """
    from main import settings
    from datetime import datetime
    string_context = obj.get_context_string(context=context)
    token = _encode_token(string_context)
    email = _encode_token(obj.email.encode())
    reset_password_url = (
        f"{settings.HOST_APP}/auth/password-reset?token={token}&id={email}"
    )
    current_year = datetime.now().year
    data = {
        "app_name": "Movy",
        "name": obj.get_name,
        "reset_password_url": reset_password_url,
        "current_year": current_year,
    }
    subject = "Password Reset"
    template_name = "user/password-reset.html"
    await send_email(
        recipients=[obj.email],
        subject=subject,
        context=data,
        template_name=template_name,
        background_task=background_tasks,
    )
