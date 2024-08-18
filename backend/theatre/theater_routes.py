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
from main.database import DB, get_db
from main.security import set_cookie

from main.decorators import PermissionDependency, Role, login_required

from .auth import TheatreAuth
from .exceptions import NameAlreadyExist
from .models import Address, Theatre, TheatreReviewRating
from .schemas import (
    ForgotPasswordResponse,
    ForgotPassWordSchema,
    ResetPasswordResponseSchema,
    ResetPasswordSchema,
    TheatreLogin,
    TheatreSignUp,
    TheatreSignUpResponse,
    VerifyTheatreAccount,
)

router = APIRouter(prefix="/auth/theatre", tags=["Theatre Auth"])


THEATRE_AUTH = TheatreAuth()


@router.post("/signup", response_model=TheatreSignUpResponse)
async def signup_theatre(
    data: TheatreSignUp,
    background_tasks: BackgroundTasks,
    db: DB = Depends(get_db),
):
    t_data = data.model_dump()
    t_data["street"] = t_data.pop("street_address")
    theatre_data = {
        "name": t_data.pop("name"),
        "description": t_data.pop("description"),
        "email": t_data.pop("email"),
        "password": t_data.pop("password"),
        "check_against": "user",
    }
    try:
        tokens, obj = await THEATRE_AUTH.register_user(
            Theatre, background_tasks, **theatre_data
        )
    except NameAlreadyExist:
        return JSONResponse(
            status_code=400,
            content={"message": "Name already taken", "status_code": 400},
        )
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"message": "Email already exists", "status_code": 400},
        )
    address = db.get_or_add(Address, **t_data, close=False)
    if address:
        address.theatres.append(obj)

    resp = JSONResponse(
        content={
            "message": "Theatre created successfully",
            "status_code": 201,
        },
        status_code=status.HTTP_201_CREATED,
    )
    tokens["status_code"] = 201
    content = TheatreSignUpResponse(**tokens).model_dump()
    resp = JSONResponse(
        content=content,
        status_code=status.HTTP_201_CREATED,
    )
    # set user refresh token
    set_cookie(resp, "refresh_token", tokens["refresh_token"], "/")
    return resp


@router.post("/verify-account")
async def verify_theatre_email(
    data: VerifyTheatreAccount,
    background_tasks: BackgroundTasks,
    db: DB = Depends(get_db),
):
    """
    verify user theatre email account
    """
    user_verified = await THEATRE_AUTH.token_verification(
        Theatre, background_tasks, **data.model_dump()
    )
    if user_verified:
        return JSONResponse(
            content={
                "message": "User successfully verified",
                "status_code": 200,
            }
        )


@router.post("/login")
async def login_theatre(data: TheatreLogin, db: DB = Depends(get_db)):
    tokens = await THEATRE_AUTH.get_login_token(data.model_dump(), Theatre)
    resp = JSONResponse(content=tokens, status_code=200)
    set_cookie(resp, "refresh_token", tokens["refresh_token"], "/")
    return resp


@router.post("/refresh")
async def theatre_refresh_token(request: Request, db: DB = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token") or ""
    return await THEATRE_AUTH.get_refresh_token(refresh_token)


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def theatre_forgot_password(
    data: ForgotPassWordSchema,
    background_tasks: BackgroundTasks,
    db: DB = Depends(get_db),
):
    da = await THEATRE_AUTH.forgot_password(Theatre, data, background_tasks)  # type: ignore
    return JSONResponse(
        content={
            "message": "Check your email for reset password links",
            "status_code": 200,
        },
        status_code=200,
    )


@router.patch("/reset-password", response_model=ResetPasswordResponseSchema)
async def theatre_reset_password(
    data: ResetPasswordSchema, db: DB = Depends(get_db)
):
    rd = await THEATRE_AUTH.reset_password(data, Theatre)
    return JSONResponse(
        content={"message": "password reset successful", "statuss_code": 200},
        status_code=200,
    )

@router.get('/me')
@login_required(Theatre)
async def get_me(request: Request, current_user = Depends(PermissionDependency(Role.THEATRE, Theatre))):
    return JSONResponse(content={"message": f"Oh my user {current_user.get_name}"})
