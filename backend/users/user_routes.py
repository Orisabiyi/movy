from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    Request,
    status,
)
from fastapi.responses import JSONResponse
from main.auth import Auth
from main.database import DB, get_db

from .models import User
from .open_apidoc import (
    forgot_password_response_doc,
    login_response_doc,
    refresh_response_doc,
    reset_password_response_doc,
    signup_response_doc,
    verify_token_response,
)
from .schemas import (
    ForgotPasswordResponseSchem,
    ForgotPasswordSchema,
    LoginResponseSchema,
    ResetPasswordSchema,
    SignUpResponseSchema,
    SignUpUserSchema,
    UserLoginInSchema,
    UserToken,
    VerifyUserToken,
)

router = APIRouter(prefix="/auth", tags=["User auth"])

AUTH = Auth()


@router.post(
    "/signup",
    status_code=201,
    response_model=SignUpResponseSchema,
    responses=signup_response_doc,  # type: ignore
)
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


@router.post(
    "/verify-account", status_code=200, responses=verify_token_response  # type: ignore
)
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
        return JSONResponse(
            content={
                "message": "email succcessfully verified",
                "status_code": 200,
            },
            status_code=200,
        )


@router.post(
    "/login", response_model=LoginResponseSchema, responses=login_response_doc  # type: ignore
)
async def user_login(data: UserLoginInSchema, db: DB = Depends(get_db)):
    return await AUTH.get_login_token(data.model_dump(), User)


@router.post("/refresh", responses=refresh_response_doc)  # type: ignore
async def refresh_token(
    refresh_token: str = Header(...), db: DB = Depends(get_db)
):
    return await AUTH.get_refresh_token(refresh_token)


# TODO user logout password endpoint


@router.post(
    "/forgot-password",
    status_code=200,
    response_model=ForgotPasswordResponseSchem,
    responses=forgot_password_response_doc,  # type: ignore
)
async def forgot_password_endpoint(
    data: ForgotPasswordSchema,
    background_tasks: BackgroundTasks,
    db: DB = Depends(get_db),
):
    await AUTH.forgot_password_(data, background_tasks)
    db._close
    return JSONResponse(
        content={
            "messaage": "Check your mail for reset password link",
            "status_code": 200,
        }
    )


@router.patch(
    "/reset-password", status_code=200, responses=reset_password_response_doc # type: ignore
)
async def reset_password_endpoint(
    data: ResetPasswordSchema, db: DB = Depends(get_db)
):
    await AUTH.reset_password(data, User)
    return JSONResponse(
        content={"message": "password reset successful", "status_code": 200},
        status_code=200,
    )


# TODO oauth2 auth endpoint
