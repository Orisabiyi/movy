from pydantic import BaseModel, EmailStr


class UserBaseSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class SignUpUserSchema(UserBaseSchema):
    password: str


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
