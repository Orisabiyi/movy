from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import JSONResponse
from main.database import DB, get_db

from .auth import TheatreAuth
from .exceptions import NameAlreadyExist
from .models import Address, Theatre, TheatreReviewRating
from .schemas import TheatreSignUp, TheatreSignUpResponse

router = APIRouter(prefix="/auth", tags=["theatre"])


THEATREAUTH = TheatreAuth()


@router.post("/theatre-central", response_model=TheatreSignUpResponse)
def signup_theatre(
    data: TheatreSignUp,
    background_tasks: BackgroundTasks,
    db: DB = Depends(get_db),
):
    t_data = data.model_dump()
    theatre_data = {
        "name": t_data.pop("name"),
        "description": t_data.pop("description"),
        "password": t_data.pop("password"),
    }
    try:
        theatre = THEATREAUTH.register_user(
            Theatre, background_tasks, **theatre_data
        )
    except NameAlreadyExist:
        return JSONResponse(
            status_code=400, content={"message": "Name already taken"}
        )
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"message": "User with email already exists"},
        )

    address = db.get_or_add(Address, **t_data)
    if address:
        address.theatres.append(theatre)

    return JSONResponse(
        content={
            "message": "Theatre created successfully",
            "status_code": 201,
        },
        status_code=status.HTTP_201_CREATED,
    )
