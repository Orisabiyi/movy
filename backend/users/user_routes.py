from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import JSONResponse
from main.auth import Auth
from main.database import DB, get_db

from .models import User
from .schemas import (
    SignUpResponseSchema,
    SignUpUserSchema,
    UserToken,
    VerifyUserToken,
)

router = APIRouter(prefix="/auth", tags=["User auth"])

AUTH = Auth()


@router.post("/signup", status_code=201, response_model=SignUpResponseSchema)
async def signup(
    data: SignUpUserSchema,
    background_tasks: BackgroundTasks,
    db: DB = Depends(get_db),
):
    try:
        await AUTH.register_user(User, background_tasks, **data.model_dump())
    except ValueError:
        message = {"message": "User with email already exists"}
        return JSONResponse(
            content=message, status_code=status.HTTP_400_BAD_REQUEST
        )

    content = SignUpResponseSchema(
        **{"message": "User created successfully", "status_code": 201}
    ).model_dump()
    return JSONResponse(
        content=content,
        status_code=status.HTTP_201_CREATED,
    )


@router.post("/account-verify", status_code=200)
async def verify_user_token_email(
    data: UserToken,
    background_tasks: BackgroundTasks,
    db: DB = Depends(get_db),
):
    """
    verify user token passed
    """
    verify_token = data.model_dump()
    verify_token["token"] = verify_token["token"].encode()
    verify_token["id"] = verify_token["id"].encode()
    is_verified = await AUTH.token_verification(
        User, background_tasks, **VerifyUserToken(**verify_token).model_dump()
    )

    if is_verified:
        return JSONResponse(content={"message": "email succcessfully verified"},status_code=200)

# TODO user login endpoint


# TODO user logout password endpoint


# TODO USER forgot password endpoint


# TODO user change password endpoint

# TODO oauth2 auth endpoint
