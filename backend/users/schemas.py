
from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from pydantic_core import PydanticCustomError
from main.security import password_is_valid
from .models import User




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
        password = password_is_valid(value)
        if not password[0]:
            raise PydanticCustomError(
                "string",
                f"{password[1]}", #type: ignore
                dict(wrong_type=value),
            )
        return value


class SignUpResponseSchema(BaseModel):
    message: str
    status_code: int


class UserToken(BaseModel):
    token: str
    id: str

class VerifyUserToken(BaseModel):
    token: bytes
    id: bytes


class UserLoginInSchema(BaseModel):
    email: EmailStr
    password: str

    
class LoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: int
    token_type: str = "Bearer"


class ForgotPasswordSchema(BaseModel):
    email: EmailStr

class ForgotPasswordResponseSchem(BaseModel):
    message: str

class ResetPasswordSchema(BaseModel):
    token: str
    id: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value, **kwargs):
        password = password_is_valid(value)
        if not password[0]:
            raise PydanticCustomError(
                "string",
                f"{password[1]}", #type: ignore
                dict(wrong_type=value),
            )
        return value