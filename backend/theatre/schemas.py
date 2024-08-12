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
    message: str