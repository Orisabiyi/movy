import base64
import logging
from datetime import datetime, timedelta, timezone
from string import (
    ascii_lowercase,
    ascii_uppercase,
    digits,
    punctuation,
    whitespace,
)
from typing import Dict, Tuple

import jwt
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from . import settings
from .database import DB
from .util_files import unique_string

ALGORITHM = "HS256"

"""
User login setup
"""

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
db = DB()


def str_encode(string: str) -> str:
    return base64.b64encode(string.encode("ascii")).decode("ascii")


def str_decode(string: str) -> str:
    return base64.b64decode(string.encode("ascii")).decode("ascii")


# decode jwt token
def get_token_payload(token: str, secret_key: str):
    payload = None
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=secret_key, algorithms=[ALGORITHM])
    except jwt.exceptions.DecodeError as e:
        raise credentials_exception
    except jwt.exceptions.ExpiredSignatureError:
        raise credentials_exception
    return payload


# generate jwt token
def generate_token_payload(
    payload: Dict, secret_key, expired_at: timedelta
) -> str:
    expiry = datetime.now() + expired_at
    payload["exp"] = expiry
    return jwt.encode(payload=payload, key=secret_key, algorithm=ALGORITHM)


async def get_current_user_or_theatre(token: str, secret_key, klass):
    payload = get_token_payload(token, secret_key)
    if payload:
        user = await load_user(klass, id=str_decode(payload.get("sub")))  # type: ignore
        if user and user.id == str_decode(payload.get("sub")):
            return user
    return None


async def load_user(klass, **kwargs):
    from sqlalchemy.exc import NoResultFound

    try:
        user = db.get(klass, **kwargs)
    except NoResultFound as e:
        logging.info(f"User not found {e}")
        user = None

    return user


# check for strong password
def password_is_valid(password: str) -> Tuple[bool, str]:
    """
    validate password meet requirement criteria

    - LEN PASSWORD > 8 and LEN PASSWORD < 50
    - PASSWORD CONTAINS lowercase and uppercase characters
    - PASSWORD CONTAINS digits
    - PASSWORD does not contain whitespace
    - PASSWORD contains punctuation characters

    RETURN true if valid else false if not valid
    """
    MAX_SIZE = 50
    MIN_SIZE = 8

    str_password = password.strip()

    len_pass = len(str_password)
    if len_pass < MIN_SIZE:
        return False, f"Provided password too short must be >= {MIN_SIZE}"
    if len_pass > MAX_SIZE:
        return False, f"Provided password too long limit <= {MAX_SIZE}"
    # valid_chars = {"-", "_", ".", "!", "@", "#", "$", "^", "&", "(", ")"}
    # invalid_chars = set(punctuation + whitespace) - valid_chars

    # for char in invalid_chars:
    #     if char in str_password:
    #         return False, f"Invalid punctuation found in password expected punctuation should be {valid_chars}"

    password_has_digits = False

    for char in digits:
        if char in str_password:
            password_has_digits = True
            break

    if not password_has_digits:
        return False, f"Password must contain atleast one or more digits"

    password_has_lowercase = False
    for char in ascii_lowercase:
        if char in str_password:
            password_has_lowercase = True
            break
    if not password_has_lowercase:
        return False, "password must contain lowercase letters"

    password_has_uppercase = False
    for char in ascii_uppercase:
        if char in str_password:
            password_has_uppercase = True
            break

    if not password_has_uppercase:
        return False, "password must contain uppercase letters"

    return True, ""


def set_cookie(resp: JSONResponse, key: str, value: str, path: str = ""):
    if key == "refresh_token":
        resp.set_cookie(
            key=key,
            value=value,
            httponly=True,
            path=path,
            expires=datetime.now(timezone.utc)
            + timedelta(minutes=settings.REFRESH_TOKEN_IN_MIN),
            samesite=None,
            secure=False
        )
