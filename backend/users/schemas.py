
from typing import Annotated
from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from pydantic_core import PydanticCustomError
from main.security import password_is_valid
from .models import User
import re

name_regex = r'^[A-Za-z]+(?:[ \-][A-Za-z]+)*$'

class UserBaseSchema(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
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

    @field_validator('first_name')
    @classmethod
    def validate_first_name_field(cls, value, **kwargs):
        if not re.match(name_regex, value):
            raise PydanticCustomError(
                "string",
                f"first name can only contain alphabet only", #type: ignore
                dict(wrong_type=value),
            )
        return value
    @field_validator('last_name')
    @classmethod
    def validate_last_name_field(cls, value, **kwargs):
        if not re.match(name_regex, value):
            raise PydanticCustomError(
                "string",
                f"last name can only contain alphabet", #type: ignore
                dict(wrong_type=value),
            )

        return value

class SignUpResponseSchema(BaseModel):
    refresh_token: str
    access_token: str
    expires_at: int
    token_type: str = "Bearer"
    status_code: int


class UserTokenSchema(BaseModel):
    token: str
    id: str

class VerifyUserToken(BaseModel):
    token: bytes
    id: bytes


class UserLoginInSchema(BaseModel):
    email: EmailStr
    password: str

class LoginResponseSchema(BaseModel):
    id: str
    name: str
    access_token: str
    refresh_token: str
    expires_at: int
    token_type: str = "Bearer"


class ForgotPasswordSchema(BaseModel):
    email: EmailStr

class ForgotPasswordResponseSchem(BaseModel):
    status_code: int
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