from datetime import datetime, timedelta
from typing import Dict

from fastapi import BackgroundTasks, HTTPException
from main import settings
from main.database import DB
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from theatre.models import Theatre, TheatreToken
from users.models import User, UserToken

from .email_context.context import (
    FORGOT_PASSWORD_CONTEXT,
    USER_VERIFICATION_ACCOUNT,
)
from .util_files import (
    _decode_token,
    _verify_hash_password,
    hash_password,
    unique_string,
)

TokeModel = {"user": UserToken, "theatre": TheatreToken}
Model = {"theatre": Theatre, "user": User}


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
        user = None
        obj = None
        try:
            user = self._db.get(klass, email=kwargs["email"])
            if user:
                raise ValueError("Email already exists")
        except NoResultFound:
            pass

        try:
            obj = self._db.get(
                Model[kwargs["check_against"]], email=kwargs["email"]
            )
            if obj:
                raise ValueError("Email already exists")
        except NoResultFound:
            ...

        del kwargs["check_against"]
        kwargs["password"] = hash_password(kwargs["password"])
        kwargs["updated_at"] = func.now()
        kwargs["is_verified"] = True
        obj = self._db.add(klass, **kwargs)
        context = USER_VERIFICATION_ACCOUNT

        #FIXME implement SMTP server
        # background_tasks.add_task(
        #     send_account_verification_email, obj, background_tasks, context
        # )
        return self._generate_token(obj, "user"), obj

    async def token_verification(
        self, klass, background_tasks: BackgroundTasks, **kwargs
    ):
        from .email import send_account_activation_email

        """
        verify both user and theatre token from request
        """
        hashed_token = _decode_token(kwargs["token"])
        email = _decode_token(kwargs["id"])

        try:
            obj = self._db.get(klass, email=email)
        except NoResultFound:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid token provided",
                    "status_code": 400,
                },
            )

        str_context = obj.get_context_string(USER_VERIFICATION_ACCOUNT)
        if not _verify_hash_password(str_context, hashed_token):
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "invalid token provided or token has expired",
                    "status_code": 400,
                },
            )
        obj.is_verified = True
        obj.updated_at = func.now()
        self._db._session.commit()
        self._db._session.refresh(obj)
        background_tasks.add_task(
            send_account_activation_email, obj, background_tasks
        )
        return self._generate_token(obj, "user"), obj

    async def get_login_token(self, data: Dict, klass):
        """
        get user login token credentials
        """
        from .security import load_user

        obj = await load_user(klass, email=data["email"])
        if not obj or not _verify_hash_password(data["password"], obj.password):
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid email or password",
                    "status_code": 400,
                },
            )
        if not obj.is_verified:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Your account is not verified please check your mail box",
                    "status_code": 400,
                },
            )
        if not obj.is_active:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Your account has been deactivated please contact admin",
                    "status_code": 400,
                },
            )

        return self._generate_token(obj, "user"), obj

    async def get_refresh_token(self, refresh_token: str):
        """
        get refresh token
        """
        from users.models import UserToken

        from .security import get_token_payload, str_decode

        pay_load = get_token_payload(
            refresh_token, settings.REFRESH_TOKEN_SECRET_KEY
        )

        if not pay_load:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid token provided",
                    "status_code": 400,
                },
            )

        rk = str_decode(pay_load.get("refresh_key"))
        ak = str_decode(pay_load.get("access_key"))

        user_id = str_decode(pay_load.get("sub"))
        kw = {"refresh_token": rk, "access_token": ak, "user_id": user_id}
        user_token = (
            self._db._session.query(UserToken)
            .options(joinedload(UserToken.user))
            .filter(
                UserToken.refresh_token == rk,
                UserToken.access_token == ak,
                UserToken.user_id == user_id,
                UserToken.expires_at > datetime.now(),
            )
            .first()
        )
        if not user_token:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid token provided",
                    "status_code": 400,
                },
            )
        user_token.expires_at = datetime.now()  # type: ignore
        self._db._session.add(user_token)
        self._db._session.commit()
        self._db._session.refresh(user_token)
        return self._generate_token(user_token.user, "user")

    async def forgot_password(
        self, klass, data, background_tasks: BackgroundTasks
    ):
        """
        handle user forgot password request
        """
        # from users.models import User

        from .email import reset_password_email

        try:
            user = self._db.get(klass, email=data.email)
        except NoResultFound:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "Email does not exists",
                    "status_code": 404,
                },
            )

        if not user.is_active:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Email has been deactivated please contact support",
                    "status_code": 400,
                },
            )
        if not user.is_verified:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Email need to be verified please check your mail",
                    "status_code": 400,
                },
            )

        context = FORGOT_PASSWORD_CONTEXT
        background_tasks.add_task(
            reset_password_email, user, background_tasks, context
        )

    async def reset_password(self, data, klass):
        """
        reset user password
        """
        token = _decode_token(data.token)
        email = _decode_token(data.id)

        try:

            user = self._db.get(klass, email=email)
        except NoResultFound:
            raise HTTPException(
                status_code=400,
                detail={"message": "invalid token passed", "status_code": 400},
            )

        str_context = user.get_context_string(FORGOT_PASSWORD_CONTEXT)

        if not _verify_hash_password(str_context, token):
            raise HTTPException(
                status_code=400,
                detail={"message": "invalid token passed", "status_code": 400},
            )
        user.password = hash_password(data.password)
        user.updated_at = func.now()
        self._db._session.add(user)
        self._db._session.commit()


    async def oauth_user_auth(self, data):
        """
        authenticate oauth user Gmail
        """
        user = self._db._session.query(User).filter(User.email == data["email"]).first()

        if user:
            if user.auth_provider != "gmail":
                return HTTPException(status_code=400, detail="Please log in with your email address")
        else:
            user = User(
                first_name=data["given_name"],
                last_name=data["family_name"],
                email=data["email"],
                password=hash_password(settings.OAUTH_PASSWORD), #type: ignore
                is_verified=True,
                auth_provider="gmail",
            )
            self._db._session.add(user)
            self._db._session.commit()
            self._db._session.refresh(user)

        return self._generate_token(user, "user"), user
 
    def _generate_token(self, user, type: str):
        # generate JWT token
        refresh_key = unique_string(100)
        access_key = unique_string(50)
        rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_IN_MIN)

        from main.security import generate_token_payload, str_encode

        user_token = None
        if type == "user":
            user_token = TokeModel[type](
                user_id=user.id,
                refresh_token=refresh_key,
                access_token=access_key,
                expires_at=datetime.now() + rt_expires,
            )
        else:
            user_token = TokeModel[type](
                theatre_id=user.id,
                refresh_token=refresh_key,
                access_token=access_key,
                expires_at=datetime.now() + rt_expires,
            )
        self._db._session.add(user_token)
        self._db._session.commit()
        self._db._session.refresh(user_token)

        at_data = {
            "sub": str_encode(str(user.id)),
            "access_key": str_encode(access_key),
            "refresh_key": str_encode(refresh_key),
            "roles": [type],
            "name": user.get_name,
        }

        expires_at = timedelta(minutes=settings.ACCESS_TOKEN_IN_MIN)

        access_token = generate_token_payload(
            at_data, settings.ACCESS_TOKEN_SECRET_KEY, expires_at
        )

        rt_data = {
            "sub": str_encode(str(user.id)),
            "access_key": str_encode(access_key),
            "refresh_key": str_encode(refresh_key),
            "name": user.get_name,
            "roles": [type],
        }
        rt_expires_at = timedelta(minutes=settings.REFRESH_TOKEN_IN_MIN)
        refresh_token = generate_token_payload(
            rt_data, settings.REFRESH_TOKEN_SECRET_KEY, rt_expires_at
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at.seconds,
        }
