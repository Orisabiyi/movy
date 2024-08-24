from datetime import datetime, timedelta
from typing import Annotated, List

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from main.database import DB, get_db
from main.decorators import PermissionDependency, Role, login_required
from movies.models import Movie
from sqlalchemy.exc import IntegrityError
from theatre.models import ShowTime, Theatre  # type: ignore

from .models import Screen, Seat
from .schemas import CreateShow, MovieList
from .utils import generate_seats

router = APIRouter(prefix="/theatre/admin", tags=["THEATRE ADMIN"])


@router.get("/movie-list", response_model=List[MovieList])
@login_required(Theatre)
async def list_of_movies_title(
    request: Request,
    db: DB = Depends(get_db),
    current_theatre=Depends(PermissionDependency(Role.THEATRE, Theatre)),
):
    movies = db._session.query(Movie).all()
    movies_lst = [
        MovieList(**{"id": movie.id, "title": movie.title}).model_dump()
        for movie in movies
    ]

    return JSONResponse(content=movies_lst, status_code=200)


@router.post("/create-movie-stream")
@login_required(Theatre)
async def theatre_movie_streams(
    request: Request,
    data: CreateShow,
    t_perm=Depends(PermissionDependency(Role.THEATRE, Theatre)),
    db: DB = Depends(get_db),
):
    """
    theatre create shows
    """
    t_perm = db._session.merge(t_perm)

    try:
        movie = db.get(Movie, id=data.movie_id)
        capacity = data.total_row_number * data.total_seat_number_in_a_row
        screen = Screen(screen_name=data.screen_name, capacity=capacity)
        db._session.add(screen)
        screen.theatre = t_perm
        db._session.commit()
    except IntegrityError as e:
        return JSONResponse(
            content={"message": "screen name for theatre cannot be duplcated"},
            status_code=400,
        )
    seat = generate_seats(
        screen, data.total_row_number, data.total_seat_number_in_a_row
    )
    db._session.add_all(seat)
    db._session.commit()

    show_time = ShowTime(
        price=data.ticket_price,
        date=data.movie_date,
        start_movie_time=data.movie_time_start,
        expires_at=data.ticket_expires_at,
    )
    show_time.screen = screen
    show_time.movies = movie
    db._session.add(show_time)
    db._session.commit()

    return JSONResponse(
        content={
            "message": "Movie streaming created by theatre sucessfully",
            "status_code": 201,
        },
        status_code=201,
    )


# @router.get("/theatre-info")
# def get_theatre_info():
#     ...