from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import JSONResponse
from main.database import DB, get_db
from .models import User
from main.auth import Auth
from .schemas import SignUpSuccessfulResponseModel, SignUpUserSchema

router = APIRouter(prefix="/auth", tags=["User auth"])

AUTH = Auth()


@router.post(
    "/signup", status_code=201, response_model=SignUpSuccessfulResponseModel
)
async def signup(data: SignUpUserSchema, background_tasks: BackgroundTasks, db: DB = Depends(get_db)):
    try:
        await AUTH.register_user(User, background_tasks, **data.model_dump())
    except ValueError:
        message = {"message": "User with email already exists"}
        return JSONResponse(
            content=message, status_code=status.HTTP_400_BAD_REQUEST
        )

    return JSONResponse(
        content={"message": "User created successfully", "status_code": 201},
        status_code=status.HTTP_201_CREATED,
    )


#TODO user login endpoint



#TODO user logout password endpoint


# TODO USER forgot password endpoint


#TODO user change password endpoint

#TODO oauth2 auth endpoint