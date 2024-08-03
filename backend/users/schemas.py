from string import (
    ascii_lowercase,
    ascii_uppercase,
    digits,
    punctuation,
    whitespace,
)

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, EmailStr, ValidationError, field_validator


def _password_is_valid(password: str) -> bool:
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

    if len(str_password) < MIN_SIZE or len(str_password) > MAX_SIZE:
        return False
    valid_chars = {"-", "_", ".", "!", "@", "#", "$", "^", "&", "(", ")"}
    invalid_chars = set(punctuation + whitespace) - valid_chars

    for char in invalid_chars:
        if char in str_password:
            return False

    password_has_digits = False

    for char in digits:
        if char in str_password:
            password_has_digits = True
            break

    if not password_has_digits:
        return False

    password_has_lowercase = False
    for char in ascii_lowercase:
        if char in str_password:
            password_has_lowercase = True
            break
    if not password_has_lowercase:
        return False

    password_has_uppercase = False
    for char in ascii_uppercase:
        if char in str_password:
            password_has_uppercase = True
            break

    if not password_has_uppercase:
        return False

    return True


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
            raise ValidationError("Invalid email address provided")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value, **kwargs):
        if not _password_is_valid(value):
            raise ValidationError("Invalid password provided")
        return value
    


class SignUpSuccessfulResponseModel(BaseModel):
    message: str
    status_code: int
