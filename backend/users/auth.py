from fastapi.exceptions import HTTPException
from main.database import DB
from passlib.hash import argon2
from sqlalchemy.exc import NoResultFound

from .models import User


def _hash_password(password: str):
    return argon2.hash(password)

def _verify_hash_password(password: str, hashed_password: str):
    return argon2.verify(password, hashed_password)



class Auth:
    def __init__(self):
        self._db = DB()

    def register_user(self, **kwargs):
        try:
            user = self._db.get(User, email=kwargs["email"])
            if user:
                raise ValueError("Invalid credential provided")
        except NoResultFound:
            kwargs['password'] = _hash_password(kwargs['password'])
            user = self._db.add(User, **kwargs)
            
        