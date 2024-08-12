from typing import List

import requests
import sqlalchemy as sa
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from main.database import DB, get_db
from movies.models import Cast, Genre, Movie
from sqlalchemy import func, text
from sqlalchemy.orm import joinedload

from .api_doc import movie_detail_response, movie_search
from .schemas import MovieDetailSchema, MovieListSchemas

router = APIRouter()


@router.get(
    "/movies/{movie_id}",
    response_model=MovieDetailSchema,
    tags=["MOVY LISTING"],
    response_description="endpoints for a detailed movie using id",
    responses=movie_detail_response, #type: ignore
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


@router.get(
    "/search/",
    tags=["MOVY LISTING"],
    response_model=List[MovieListSchemas],
    responses=movie_search, #type: ignore
)
def search_movies(
    request: Request,
    query: str = Query(
        ...,
        description="the search query to match movie titles and descriptions",
    ),
    db: DB = Depends(get_db),
):
    """
    perform search on movie by title
    """
    search_query = text(
        "SELECT * FROM movies WHERE MATCH(title, description, tag_line) AGAINST(:query IN BOOLEAN MODE)"
    )
    results = db._session.execute(search_query, {"query": query}).fetchall()
    if not results:
        return JSONResponse(
            content={
                "message": f"Movie with query {query} not found",
                "status_code": 404,
            },
            status_code=404,
        )

    movie_lst = [
        MovieListSchemas(
            **{
                "id": movie.id,
                "title": movie.title,
                "tagline": movie.tag_line,
                "poster_path": movie.poster_path,
                "runtime": f"{movie.duration_in_min // 60}hr {movie.duration_in_min % 60}min",
                "release_date": str(movie.release_date),
                "url": f"{request.base_url}movies/{movie.id}",
            }
        ).model_dump()
        for movie in results
    ]

    return JSONResponse(content=movie_lst, status_code=200)


# @router.get('/upcoming-movies')
# def get_upcoming_movies(db: DB = Depends(get_db)):
#     #TODO implement the get movie endpoint
#     ...


@router.get("/genres/")
def get_movie_list_genres():
    ...
    # TODO return a list of genrers


# TODO filter by genrers

# TODO filter by date


# TODO Movie Schedule
