from typing import Dict

from cryptography.fernet import Fernet
from fastapi import BackgroundTasks, HTTPException
from main.database import DB
from passlib.hash import argon2
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound

from .email_context.context import USER_VERIFICATION_ACCOUNT


def hash_password(password: str):
    return argon2.hash(password)


def _verify_hash_password(password: str, hashed_password: str):
    return argon2.verify(password, hashed_password)


def _decode_token(encrpt: bytes) -> str:
    from main import settings

    cypher_token = Fernet(settings.KEY)
    return cypher_token.decrypt(encrpt).decode()


class Auth:
    def __init__(self):
        self._db = DB()

    async def register_user(
        self, klass, background_tasks: BackgroundTasks, **kwargs
    ):
        from .email import send_account_verification_email

        """
        register user account details
        """
        try:
            user = self._db.get(klass, email=kwargs["email"])
            if user:
                raise ValueError("Invalid credential provided")
        except NoResultFound:
            pass

        kwargs["password"] = hash_password(kwargs["password"])
        obj = self._db.add(klass, **kwargs, close=False)
        obj.updated_at = func.now()
        self._db._session.commit()
        context = USER_VERIFICATION_ACCOUNT

        background_tasks.add_task(
            send_account_verification_email, obj, background_tasks, context
        )

        return obj

    async def token_verification(
        self, klass, background_tasks: BackgroundTasks, **kwargs
    ):
        from .email import send_account_activation_email
        """
        verify both user and theatre token from request
        """
        hashed_token = _decode_token(kwargs["token"])
        print(hashed_token)
        email = _decode_token(kwargs["id"])

        try:
            obj = self._db.get(klass, email=email)
        except NoResultFound:
            raise HTTPException(
                status_code=400, detail={"message": "Invalid token provided", "status_code": 400}
            )

        str_context = obj.get_context_string(USER_VERIFICATION_ACCOUNT)

        if not _verify_hash_password(str_context, hashed_token):
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "invalid token provided or token has expired",
                    "status_code": 400
                },
            )
        obj.is_verified = True
        obj.updated_at = func.now()
        self._db._session.commit()
        self._db._session.refresh(obj)

        background_tasks.add_task(send_account_activation_email, obj, background_tasks)
        return True