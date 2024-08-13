from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import JSONResponse
from main import settings
from main.database import DB, get_db

from .auth import TheatreAuth
from .exceptions import NameAlreadyExist
from .models import Address, Theatre, TheatreReviewRating
from .schemas import TheatreSignUp, TheatreSignUpResponse, VeriifyTheatreAccount

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
    }
    try:
        tokens, obj = await THEATRE_AUTH.register_user(
            Theatre, background_tasks, **theatre_data
        )
    except NameAlreadyExist:
        return JSONResponse(
            status_code=400, content={"message": "Name already taken", "status_code": 400}
        )
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"message": "User with email already exists", "status_code": 400},
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
    print(tokens)
    tokens["status_code"] = 201
    content = TheatreSignUpResponse(**tokens).model_dump()
    resp = JSONResponse(
        content=content,
        status_code=status.HTTP_201_CREATED,
    )
    # set user refresh token
    resp.set_cookie(
        "refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        path="/auth/refresh",
        expires=datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_IN_MIN),
    )
    # set user access token cookies
    resp.set_cookie(
        "access_token",
        value=tokens["access_token"],
        httponly=True,
        expires=datetime.now(timezone.utc)
        + timedelta(minutes=settings.ACCESS_TOKEN_IN_MIN),
    )
    return resp


@router.post("/verify-account")
async def verify_theatre_email(data: VeriifyTheatreAccount, background_tasks: BackgroundTasks,db: DB = Depends(get_db)):
    """
    verify user theatre email account
    """
    return await THEATRE_AUTH.token_verification(Theatre, background_tasks, **data.model_dump()) 


@router.post('/refresh-token')
def theatre_refresh_token():
    ...