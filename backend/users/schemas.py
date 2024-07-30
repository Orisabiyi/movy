from pydantic import BaseModel





class UserBaseSchema(BaseModel):
    first_name: str
    last_name: str
    email: str


class SignUpUserSchema(UserBaseSchema):
    password: str


class SignUpSuccessfulResponseModel(BaseModel):
    message: str
    status_code: int