from string import (
    ascii_lowercase,
    ascii_uppercase,
    digits,
    punctuation,
    whitespace,
)
from typing import Tuple

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core import PydanticCustomError

from .models import User


def _password_is_valid(password: str) -> Tuple[bool, str]:
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


class UserBaseSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class SignUpUserSchema(UserBaseSchema):
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value, **kwargs):
        """
        validate user email address
        """
        try:
            email = validate_email(value)
        except EmailNotValidError:
            raise PydanticCustomError(
                "string",
                "Invalid email address provided",
                dict(wrong_type=value),
            )
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value, **kwargs):
        password = _password_is_valid(value)
        if not password[0]:
            raise PydanticCustomError(
                "string",
                f"{password[1]}",
                dict(wrong_type=value),
            )
        return value


class SignUpSuccessfulResponseModel(BaseModel):
    message: str
    status_code: int
