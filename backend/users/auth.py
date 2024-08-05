from fastapi.exceptions import HTTPException
from sqlalchemy import func
from main.database import DB
from passlib.hash import argon2
from sqlalchemy.exc import NoResultFound
from .email import send_account_verification_email
from .models import User
from fastapi import BackgroundTasks


def hash_password(password: str):
    return argon2.hash(password)

def _verify_hash_password(password: str, hashed_password: str):
    return argon2.verify(password, hashed_password)



class Auth:
    def __init__(self):
        self._db = DB()

    async def register_user(self, background_tasks: BackgroundTasks, **kwargs):
        try:
            user = self._db.get(User, email=kwargs["email"])
            print(user)
            if user:
                raise ValueError("Invalid credential provided")
        except NoResultFound:
            pass

        kwargs['password'] = hash_password(kwargs['password'])
        user = self._db.add(User, **kwargs, close=False)
        user.updated_at = func.now()
        self._db._session.commit()
        context = "verify-email"

        background_tasks.add_task(send_account_verification_email, user, background_tasks, context)

        return user
            
        