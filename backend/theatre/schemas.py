from datetime import date, time
from pydantic import BaseModel, EmailStr
from typing import Optional




class TheatreBase(BaseModel):
    name: str
    email: EmailStr
    description: Optional[str] = None
    state: str
    city: str
    street_address: str

class TheatreSignUp(TheatreBase):
    password: str

class TheatreSignUpResponse(BaseModel):
    status_code: int
    access_token: str
    refresh_token: str
    expires_at: int

class TheatreLogin(BaseModel):
    email: EmailStr
    password: str


class TheatreLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: int

class VerifyTheatreAccount(BaseModel):
    id: str
    token: str

class ForgotPassWordSchema(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str
    status_code: int


class ResetPasswordSchema(BaseModel):
    id: str
    token: str
    password: str

class ResetPasswordResponseSchema(ForgotPasswordResponse):
   ... 



class CreateShowTimeResponse(BaseModel):
    ...

