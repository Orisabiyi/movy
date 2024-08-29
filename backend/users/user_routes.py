from datetime import datetime, timedelta, timezone

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, BackgroundTasks, Depends, Header, Request, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from main import settings
from main.auth import Auth
from main.database import DB, get_db
from main.decorators import PermissionDependency, Role, login_required
from main.security import set_cookie
from starlette.requests import Request

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

templates = Jinja2Templates(directory="templates")

oauth = OAuth()

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=settings.GOOGLE_CLIENT_ID, #type: ignore
    client_secret=settings.GOOGLE_CLIENT_SECRET,#type: ignore
    client_kwargs={
        "scope": "email openid profile",
        "redirect_url": "http://localhost:8000/auth",
    },
)


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
    except ValueError as e:
        print(e)
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
    )  # type: ignore
    data = {
        "id": obj.id,
        "name": obj.get_name,
        "refresh_token": token["refresh_token"],
        "access_token": token["access_token"],
    }  # type: ignore
    resp = JSONResponse(content=data, status_code=200)
    set_cookie(resp, "refresh_token", token["refresh_token"], "/")
    return resp


@router.post(
    "/login", response_model=LoginResponseSchema, responses=login_response_doc  # type: ignore
)
async def user_login(data: UserLoginInSchema, db: DB = Depends(get_db)):
    tokens, obj = await AUTH.get_login_token(data.model_dump(), User)
    data = {
        "id": obj.id,  # type: ignore
        "name": obj.get_name,  # type: ignore
        "refresh_token": tokens["refresh_token"],  # type: ignore
        "access_token": tokens["access_token"],  # type:ignore
    }  # type: ignore
    resp = JSONResponse(content=data, status_code=200)
    set_cookie(resp, "refresh_token", tokens["refresh_token"], "/")  # type: ignore
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


@router.get("/google/login")
async def login(request: Request):
    url = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, url) #type: ignore


@router.get("/callback/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request) #type: ignore
    except OAuthError as e:
        return JSONResponse(content={"message": f"{e.error}"}, status_code=400)

    user = token.get("userinfo")
    if not user:
        ...
    request.session["user"] = dict(user)
    token, user = await AUTH.oauth_user_auth(dict(user)) #type: ignore

    resp = JSONResponse(
        content={
            "id": user.id,
            "access_token": token["access_token"],
            "refresh_token": token["refresh_token"],
        },
        status_code=200
    )
    set_cookie(resp, "refresh_token", token["refresh_token"])
    return resp


@router.get("/home")
def index(request: Request):
    return templates.TemplateResponse(
        name="home.html", context={"request": request}
    )
