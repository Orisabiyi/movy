from datetime import datetime, timedelta
from typing import Annotated, List

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from main.database import DB, get_db
from main.decorators import PermissionDependency, Role, login_required
from movies.models import Movie
from theatre.models import ShowTime, Theatre  # type: ignore

from .models import Screen, Seat
from .schemas import CreateShow, MovieList
from .utils import generate_seats

router = APIRouter(prefix="/theatre", tags=["THEATRE MANAGEMENT"])


t_permission = Annotated[
    PermissionDependency, Depends(PermissionDependency(Role.THEATRE, Theatre))
]


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


# @router.post("/create-movie-stream")
# @login_required(Theatre)
# def theatre_movie_streams(
#     request: Request,
#     data: CreateShow,
#     t_perm=Depends(PermissionDependency(Role.THEATRE, Theatre)),
#     db: DB = Depends(get_db),
# ):
#     """
#     theatre create shows
#     """
#     print(t_perm)
#     movie = db.get(Movie, id=data.movie_id)
#     screen = db.add(
#         Screen,
#         close=False,
#         screen_name=data.screen_name,
#         capacity=data.capacity,
#     )
#     print(screen.theatre)
#     screen.theatre.append(t_perm)
#     seat = generate_seats(
#         screen, data.total_row_number, data.total_seat_number_in_a_row
#     )
#     db._session.add_all(seat)
#     db._session.commit()

#     end_show_time = datetime.combine(
#         data.movie_date, data.movie_time_start
#     ) + timedelta(minutes=movie.duration_in_min)
#     show_time = ShowTime(
#         start_movie_time=data.movie_time_start,
#         end_movie_time=end_show_time.time(),
#     )
#     show_time.append(screen)
#     show_time.append(movie)
#     db._session.add(show_time)
#     db._session.commit()

#     return JSONResponse(
#         content={
#             "message": "Movie steaming crete by theatre sucessfully",
#             "status_code": 201,
#         },
#         status_code=201,
#     )


# @router.post("/")
