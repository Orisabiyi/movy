from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from main.database import DB, get_db

from .auth import Auth
from .schemas import SignUpSuccessfulResponseModel, SignUpUserSchema

router = APIRouter(prefix="/auth")

AUTH = Auth()


@router.post(
    "/signup", status_code=201, response_model=SignUpSuccessfulResponseModel
)
def signup(data: SignUpUserSchema, db: DB = Depends(get_db)):
    try:
        AUTH.register_user(**data.model_dump())
    except ValueError:
        message = {"message": "Invalid credential provided"}
        return JSONResponse(
            content=message, status_code=status.HTTP_400_BAD_REQUEST
        )


    #TODO send user verification email
    
    return JSONResponse(
        content={"message": "User created successfully"},
        status_code=status.HTTP_201_CREATED,
    )

