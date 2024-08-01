from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from main.database import DB, get_db
from movies.models import Cast, Genre, Movie, ProductionCompany
from sqlalchemy.orm import joinedload
import requests
from .api_doc import movie_detail_response
from .schemas import MovieDetailSchema

router = APIRouter()


@router.get(
    "/movies/{movie_id}",
    response_model=MovieDetailSchema,
    tags=["MOVY LISTING"],
    response_description="endpoints for a detailed movie using id",
    responses=movie_detail_response,
)
def get_movie_detail(movie_id: int, db: DB = Depends(get_db)):

    movie = (
        db._session.query(Movie)
        .options(
            joinedload(Movie.movie_casts).joinedload(Cast.casts_movie),
            joinedload(Movie.movie_genres).joinedload(Genre.genre_movies),
        )
        .filter(Movie.id == movie_id)
        .first()
    )
    if not movie:
        return JSONResponse(
            status_code=404,
            content={"message": "Movie with this id not found"},
        )
    data = MovieDetailSchema(**movie.movie_to_dict()).model_dump()
    return JSONResponse(content=data, status_code=200)


# @router.get('/upcoming-movies')
# def get_upcoming_movies(db: DB = Depends(get_db)):
#     #TODO implement the get movie endpoint
#     ...
