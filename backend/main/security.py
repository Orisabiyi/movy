from datetime import datetime, timedelta
import logging
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from .database import DB
from string import (
    ascii_lowercase,
    ascii_uppercase,
    digits,
    punctuation,
    whitespace,
)
import base64
import jwt
from . import settings

from typing import Tuple, Dict
from .utils import unique_string


ALGORITHM = "HS256"

"""
User login setup
"""

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
db = DB()

def str_encode(string: str) -> str:
    return base64.b64encode(string.encode('ascii')).decode('ascii')

def str_decode(string: str) -> str:
    return base64.b64decode(string.encode('ascii')).decode('ascii')


# decode jwt token
def get_token_payload(token: str, secret_key: str):
    payload = None
    try:
        payload = jwt.decode(token, key=secret_key, algorithms=[ALGORITHM])
    # except jwt.exceptions.DecodeError:
    #     raise HTTPException(status_code=400, detail= {"message": "Invalid token provided or token expired"})
    except Exception as jwt_except:
        logging.debug(f"JWT Error {str(jwt_except)}")
    return payload

# generate jwt token
def generate_token_payload(payload: Dict, secret_key,expired_at: timedelta) -> str:
    expiry = datetime.now() + expired_at
    payload["exp"] = expiry
    return jwt.encode(payload=payload, key=secret_key, algorithm=ALGORITHM)



async def get_token_user(token: str, secret_key, klass):
    payload = get_token_payload(token, secret_key)
    if payload:
        user = await load_user(int(str_decode(payload.get('sub'))), klass)
        if user and user.id == int(payload.get('sub')):
            return user
    return None

async def load_user(uni, klass):
    from sqlalchemy.exc import NoResultFound
    try:
        user = db.get(klass, email=uni)
    except NoResultFound:
        logging.info(f"User not found, Email {uni}")
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
    valid_chars = {"-", "_", ".", "!", "@", "#", "$", "^", "&", "(", ")"}
    invalid_chars = set(punctuation + whitespace) - valid_chars

    for char in invalid_chars:
        if char in str_password:
            return False, f"Invalid punctuation found in password expected punctuation should be {valid_chars}"

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