from datetime import datetime, timedelta, timezone

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    Request,
    status,
)
from fastapi.responses import JSONResponse
from main import settings
from main.auth import Auth
from main.database import DB, get_db
from main.decorators import PermissionDependency, Role, login_required
from main.security import set_cookie

from .models import User, UserToken
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
    UserTokenSchema,
    VerifyUserToken,
)

router = APIRouter(prefix="/auth/user", tags=["User auth"])

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
    u_data = data.model_dump()
    u_data["check_against"] = "theatre"
    try:
        tokens, obj = await AUTH.register_user(
            User, background_tasks, **u_data
        )
    except ValueError:
        message = {"message": "Email already exists"}
        return JSONResponse(
            content=message, status_code=status.HTTP_400_BAD_REQUEST
        )
    tokens["status_code"] = 201
    content = SignUpResponseSchema(**tokens).model_dump()
    resp = JSONResponse(
        content=content,
        status_code=status.HTTP_201_CREATED,
    )
    # set user refresh token
    set_cookie(resp, "refresh_token", tokens["refresh_token"], "/")
    return resp


@router.post(
    "/verify-account", status_code=200, responses=verify_token_response  # type: ignore
)
async def verify_user_token_email(
    data: UserTokenSchema,
    background_tasks: BackgroundTasks,
    db: DB = Depends(get_db),
):
    """
    verify user token passed
    """
    verify_token = data.model_dump()
    verify_token["token"] = verify_token["token"].encode()
    verify_token["id"] = verify_token["id"].encode()
    token, obj = await AUTH.token_verification(
        User, background_tasks, **VerifyUserToken(**verify_token).model_dump()
    )
    data = {
        "id": obj.id,
        "name": obj.get_name,
        "refresh_token": token["refresh_token"],
        "access_token": token["access_token"],
    }
    resp = JSONResponse(content=data, status_code=200)
    set_cookie(resp, "refresh_token", token["refresh_token"], "/")
    return resp


@router.post(
    "/login", response_model=LoginResponseSchema, responses=login_response_doc  # type: ignore
)
async def user_login(data: UserLoginInSchema, db: DB = Depends(get_db)):
    tokens, obj = await AUTH.get_login_token(data.model_dump(), User)
    data = {
        "id": obj.id,
        "name": obj.get_name,
        "refresh_token": tokens["refresh_token"],
        "access_token": tokens["access_token"],
    }
    resp = JSONResponse(content=data, status_code=200)
    set_cookie(resp, "refresh_token", tokens["refresh_token"], "/")
    return resp


@router.post("/refresh", responses=refresh_response_doc)  # type: ignore
async def refresh_token(request: Request, db: DB = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token") or ""
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
    await AUTH.forgot_password(User, data, background_tasks)  # type: ignore
    return JSONResponse(
        content={
            "messaage": "Check your mail for reset password link",
            "status_code": 200,
        }
    )


@router.patch(
    "/reset-password", status_code=200, responses=reset_password_response_doc  # type: ignore
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

# @router.get('/me')
# @login_required(User)
# async def get_me(request: Request, current_user = Depends(PermissionDependency(Role.USER, User))):
#     return JSONResponse(content={"message": f"Oh my user {current_user.get_name}"})
