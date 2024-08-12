from datetime import datetime, timedelta
from typing import Dict

from fastapi import BackgroundTasks, HTTPException
from main import settings
from main.database import DB
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from .email_context.context import USER_VERIFICATION_ACCOUNT, FORGOT_PASSWORD_CONTEXT
from .utils import unique_string, _decode_token, _verify_hash_password, hash_password




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
        return True

    async def get_login_token(self, data, klass):
        """
        get user login token credentials
        """
        from .security import load_user

        user = await load_user(data["email"], klass)
        if not user:
            raise HTTPException(
                status_code=400,
                detail={"message": "Invalid email or password"},
            )
        if not _verify_hash_password(data["password"], user.password):
            raise HTTPException(
                status_code=400,
                detail={"message": "Invalid email or password"},
            )
        if not user.is_verified:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Your account is not verified please check your mail box"
                },
            )
        if not user.is_active:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Your account has been deactivated please contact admin"
                },
            )

        return self._generate_token(user)

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
                status_code=400, detail={"message": "Invalid token provided"}
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
                status_code=400, detail={"message": "Invalid token provided"}
            )
        user_token.expires_at = datetime.now() #type: ignore
        self._db._session.add(user_token)
        self._db._session.commit()
        self._db._session.refresh(user_token)
        return self._generate_token(user_token.user)

    async def forgot_password_(self, data, background_tasks: BackgroundTasks):
        """
        handle user forgot password request
        """
        from users.models import User
        from .email import reset_password_email
        try:
            user = self._db.get(User, email=data.email)
        except NoResultFound:
            raise HTTPException(status_code=404, detail={"message": "Email does not exists"})

        if not user.is_active:
            raise HTTPException(status_code=400, detail={"message": "Email has been deactivated please contact support"})

        if not user.is_verified:
            raise HTTPException(status_code=400, detail={"message": "Email need to be verified please check your mail"})

        context = FORGOT_PASSWORD_CONTEXT
        background_tasks.add_task(reset_password_email, user, background_tasks, context)

    async def reset_password(self, data, klass):
        """
        reset user password
        """
        token = _decode_token(data.token)
        email = _decode_token(data.id)

        try:
            
            user = self._db.get(klass, email=email)
        except NoResultFound:
            raise HTTPException(status_code=400, detail={"message": "invalid token passed"})

        str_context = user.get_context_string(FORGOT_PASSWORD_CONTEXT)

        if not _verify_hash_password(str_context, token):
            raise HTTPException(status_code=400, detail={"message": "invalid token passed"})
        user.password = hash_password(data.password)
        user.updated_at = func.now()
        self._db._session.add(user)
        self._db._session.commit()
 
    def _generate_token(self, user):
        # generate JWT token
        refresh_key = unique_string(100)
        access_key = unique_string(50)

        rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_IN_MIN)

        from main.security import generate_token_payload, str_encode
        from users.models import UserToken

        user_token = UserToken(
            user_id=user.id,
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
            "roles": ["user"],
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
            "roles": ["user"],
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
