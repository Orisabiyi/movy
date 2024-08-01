from pydantic import BaseModel, EmailStr





class UserBaseSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class SignUpUserSchema(UserBaseSchema):
    password: str


class SignUpSuccessfulResponseModel(BaseModel):
    message: str
    status_code: int