from fastapi import BackgroundTasks
from main.auth import Auth
from sqlalchemy.exc import NoResultFound
from .exceptions import NameAlreadyExist
from .models import TheatreToken
from fastapi import HTTPException
from main import settings
from datetime import datetime
from sqlalchemy.orm import joinedload


class TheatreAuth(Auth):
    async def register_user(self, klass, background_tasks: BackgroundTasks, **kwargs):
        try:
            theatre = self._db._session.query(klass).filter_by(name=kwargs["name"]).first()
            if theatre:
                raise NameAlreadyExist()
        except NoResultFound:
            pass
        return await super().register_user(klass, background_tasks, **kwargs) #type ignore

    async def get_refresh_token(self, refresh_token: str):
        """
        get refresh token
        """
        from main.security import get_token_payload, str_decode

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
            self._db._session.query(TheatreToken)
            .options(joinedload(TheatreToken.theatre))
            .filter(
                TheatreToken.refresh_token == rk,
                TheatreToken.access_token == ak,
                TheatreToken.theatre_id == user_id,
                TheatreToken.expires_at > datetime.now(),
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
        return self._generate_token(user_token.theatre, "theatre")

    async def get_login_token(self, data, klass):
        return await super().get_login_token(data, klass)

    def _generate_token(self, user, type: str):
        return super()._generate_token(user, "theatre")