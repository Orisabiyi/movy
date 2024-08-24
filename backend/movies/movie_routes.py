from datetime import datetime
import json
from decimal import Decimal
from typing import List

import requests
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from main.database import DB, get_db
from main.decorators import PermissionDependency, login_required
from main.hash_id import decode_id, encode_id
from main.m_db import REDIS_CLI
from sqlalchemy import func, select, text
from sqlalchemy.future import select
from sqlalchemy.orm import aliased, contains_eager, joinedload
from theatre.models import ShowTime, Theatre
from theatre.theatre_management.models import Screen, Seat

from .api_doc import get_movie_by_theatre, movie_detail_response, movie_search
from .models import Cast, Genre, Movie, movie_cast, movie_genre
from .schemas import (
    GenreList,
    MovieDetailSchema,
    MovieListSchemas,
    MovieTheatreSchema,
)

# from users.models import User
from .utils import movie_schema_list

router = APIRouter(prefix="/movies", tags=["MOVY LISTING"])


@router.get(
    "/{movie_id}",
    response_model=MovieDetailSchema,
    response_description="Endpoints for a detailed movie using ID",
    responses=movie_detail_response,  # type: ignore
)
def get_movie_detail(movie_id: str, db: DB = Depends(get_db)):

    # Decode the movie ID
    movie_id = decode_id(movie_id) # type: ignore

    # Try fetching the movie details from Redis
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

        # Main query to fetch the movie with limited cast details (using outerjoin to make cast retrieval optional)
        movie = (
            db._session.query(Movie)
            .outerjoin(movie_cast, Movie.id == movie_cast.c.movie_id)
            .outerjoin(Cast, movie_cast.c.cast_id == Cast.id)
            .filter(Movie.id == movie_id)
            .options(contains_eager(Movie.movie_casts))
            # .first()
        )

        if not movie:
            return JSONResponse(
                status_code=404,
                content={"message": "Movie with this ID not found"},
            )

        # Prepare the movie details
        for movie in movie:
            movie_dict = {
                "id": encode_id(movie.id), #type:ignore
                "title": movie.title,
                "description": movie.description,
                "poster_path": movie.poster_path,
                "backdrop_path": movie.backdrop_path,
                "tag_line": movie.tag_line,
                "trailer_link": movie.trailer_link,
                "runtime": f"{movie.duration_in_min // 60}hr {movie.duration_in_min % 60}min",
                "release_date": str(movie.release_date),
                "genres": [genre.name for genre in movie.movie_genres],
                "starring": (
                    [
                        {"poster_path": cast.profile_path, "name": cast.name}
                        for cast in movie.movie_casts
                    ]
                    if movie.movie_casts
                    else []
                ),  # Ensure an empty list if no cast members are present
            }

        # Add the data to Redis
        data = MovieDetailSchema(**movie_dict)
        REDIS_CLI.set(f"movie_{movie_id}", data.model_dump_json())
    else:
        # Load the movie data from Redis if it was cached
        data = MovieDetailSchema(**json.loads(get_movie.decode("UTF-8")))  # type: ignore

    # Return the movie details
    return JSONResponse(content=data.model_dump(), status_code=200)


@router.get(
    "/search/",
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
                "id": encode_id(movie.id),
                "title": movie.title,
                "tagline": movie.tag_line,
                "poster_path": movie.poster_path,
                "runtime": f"{movie.duration_in_min // 60}hr {movie.duration_in_min % 60}min",
                "description": movie.description,
                "release_date": str(movie.release_date),
                "url": f"{request.base_url}movies/{encode_id(movie.id)}",
            }
        ).model_dump()
        for movie in results
    ]
    return JSONResponse(content=movie_lst, status_code=200)


    

@router.get(
    "/genres/", response_model=List[GenreList], summary="list all moie genres"
)
def get_movie_list_genres(db: DB = Depends(get_db)):
    """
    list all movie genres
    """
    query = db._session.query(Genre).all()
    genre_list = [
        GenreList(**{"id": genre.id, "name": genre.name}).model_dump()
        for genre in query
    ]
    return JSONResponse(status_code=200, content=genre_list)


@router.get(
    "/", response_model=MovieListSchemas, summary="filter movie by genre"
)
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


@router.get(
    "/{movie_id}/theatre",
    status_code=200,
    summary="Get theatres showing the movie",
    description="Detailed information about theatres showing a movie.",
    responses=get_movie_by_theatre,  # type: ignore
)
def get_theatres_streaming_movie(movie_id: str, db: DB = Depends(get_db)):
    """
    get all theatres that are streaming the movies
    """
    movie_id = decode_id(movie_id) #type: ignore
    movie = (
        db._session.query(Movie)
        .options(
            joinedload(Movie.show_times)
            .joinedload(ShowTime.screen)
            .joinedload(Screen.theatre)
        )
        .filter(Movie.id == movie_id)
        .first()
    )

    if not movie:
        return JSONResponse(
            content={"message": "movie with id not found"}, status_code=404
        )
    movie_theatres = {
        "movie_id": encode_id(movie.id), #type: ignore
        "theatres": [],
    }

    theatres_dict = {}
    for showtime in movie.show_times:
        screen = showtime.screen
        theatre = screen.theatre

        if theatre.id not in theatres_dict:
            theatres_dict[theatre.id] = {
                "theatre_id": theatre.id,
                "theatre_name": theatre.name,
                "screens": [],
            }

        screen_dict = next(
            (
                s
                for s in theatres_dict[theatre.id]["screens"]
                if s["screen_id"] == encode_id(screen.id)
            ),
            None,
        )
        if not screen_dict:
            screen_dict = {
                "screen_id": encode_id(screen.id),
                "screen_name": screen.screen_name,
                "capacity": screen.capacity,
                "seats": [
                    {
                        "seat_id": encode_id(seat.id),
                        "row": seat.row,
                        "seat_number": seat.seat_number,
                        "is_available": seat.is_available,
                    }
                    for seat in screen.seats
                ],
                "showtimes": [],
            }
            theatres_dict[theatre.id]["screens"].append(screen_dict)

        screen_dict["showtimes"].append(
            {
                "showtime_id": encode_id(showtime.id),
                "movie_date": showtime.date,  # Format datetime
                "movie_start_time": showtime.start_movie_time,
                "price": showtime.price,  # Convert Decimal to float
            }
        )
    movie_theatres["theatres"] = list(theatres_dict.values())
    return movie_theatres


# TODO filter by date
# @router.get("/date")
# def filter_movies_by_year(
#     year: int = Query(...),
#     month: str = Query(None),
#     day: str = Query(None),
#     db: DB = Depends(get_db),
# ): ...


# TODO filter movie by theatre show time


# TODO Movie Schedule
