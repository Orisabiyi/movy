import json
from typing import List

import requests
import sqlalchemy as sa
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination, paginate
from main.database import DB, get_db
from main.m_db import REDIS_CLI
from main.pagination import CustomParams, get_custom_page
from sqlalchemy import func, select, text
from sqlalchemy.orm import aliased, contains_eager, joinedload, subqueryload

from .api_doc import movie_detail_response, movie_search
from .models import Cast, Genre, Movie, movie_cast, movie_genre
from .schemas import GenreList, MovieDetailSchema, MovieListSchemas
from .utils import movie_schema_list

router = APIRouter(prefix="/movies")


@router.get(
    "/{movie_id}",
    response_model=MovieDetailSchema,
    tags=["MOVY LISTING"],
    response_description="endpoints for a detailed movie using id",
    responses=movie_detail_response,  # type: ignore
)
def get_movie_detail(movie_id: int, db: DB = Depends(get_db)):

    # get value from redis
    get_movie = REDIS_CLI.get(f"movie_{movie_id}")  # type: ignore
    if not get_movie:
        CastAlias = aliased(Cast)
        # Subquery to get limited cast IDs for the movie
        limited_casts_subquery = (
            select(movie_cast.c.cast_id)
            .filter(movie_cast.c.movie_id == movie_id)
            .limit(10)
            .subquery()
        )
        # Main query to fetch the movie with limited cast details
        movie_with_limited_casts = (
            db._session.query(Movie)
            .join(movie_cast, Movie.id == movie_cast.c.movie_id)
            .join(Cast, movie_cast.c.cast_id == Cast.id)
            .filter(Movie.id == movie_id)
            .filter(
                Cast.id.in_(select(limited_casts_subquery.c.cast_id))
            )  # Ensure only the limited cast IDs are used
            .options(contains_eager(Movie.movie_casts))
            .all()
        )
        if not movie_with_limited_casts:
            return JSONResponse(
                status_code=404,
                content={"message": "Movie with this id not found"},
            )
        # Extract and print cast details
        movie_dict = {}
        for movie in movie_with_limited_casts:
            movie_dict = {
                "id": movie.id,
                "title": movie.title,
                "description": movie.description,
                "poster_path": movie.poster_path,
                "backdrop_path": movie.backdrop_path,
                "tag_line": movie.tag_line,
                "trailer_link": movie.trailer_link,
                "runtime": f"{movie.duration_in_min // 60}hr {movie.duration_in_min % 60}min",
                "release_date": str(movie.release_date),
                "genres": [genre.name for genre in movie.movie_genres],
                "starring": [
                    {"poster_path": cast.profile_path, "name": cast.name}
                    for cast in movie.movie_casts
                ],
            }
        # add the data to the redis server
        data = MovieDetailSchema(**movie_dict)
        REDIS_CLI.set(f"movie_{movie_id}", data.model_dump_json())
    else:

        data = MovieDetailSchema(**json.loads(get_movie.decode("UTF-8")))  # type: ignore
    return JSONResponse(content=data.model_dump(), status_code=200)


@router.get(
    "/search/",
    tags=["MOVY LISTING"],
    response_model=List[MovieListSchemas],
    responses=movie_search,  # type: ignore
)
def search_movies(
    request: Request,
    query: str = Query(
        ...,
        description="the search query to match movie titles and descriptions",
    ),
    db: DB = Depends(get_db),
    params: CustomParams = Depends(),
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
    return JSONResponse(content=movie_cast, status_code=200)


# @router.get('/upcoming-movies')
# def get_upcoming_movies(db: DB = Depends(get_db)):
#     #TODO implement the get movie endpoint
#     ...


@router.get("/genres/", response_model=List[GenreList])
def get_movie_list_genres(db: DB = Depends(get_db)):
    query = db._session.query(Genre).all()
    genre_list = [
        GenreList(**{"id": genre.id, "name": genre.name}).model_dump()
        for genre in query
    ]
    return JSONResponse(status_code=200, content=genre_list)


@router.get("/", response_model=MovieListSchemas)
def filter_movies_by_genres(
    request: Request,
    genre: str = Query(..., description="get movie all movies by genres"),
    db: DB = Depends(get_db),
):
    """
    get all movie by genres
    """
    movies = (
        db._session.query(Movie)
        .join(movie_genre, Movie.id == movie_genre.c.movie_id)
        .join(Genre, Genre.id == movie_genre.c.genre_id)
        .filter(Genre.name == genre)
        .all()
    )

    if not movies:
        return JSONResponse(
            content={"message": "Movie with genre not  Found"}, status_code=401
        )

    movie_list = [
        movie.model_dump() for movie in movie_schema_list(request, movies)
    ]

    return JSONResponse(status_code=200, content=movie_list)


#TODO filter by date
@router.get("/date")
def filter_movies_by_year(
    year: int = Query(...),
    month: str = Query(None),
    day: str = Query(None),
    db: DB = Depends(get_db),
): ...


# TODO filter movie by theatre show time


# TODO Movie Schedule
