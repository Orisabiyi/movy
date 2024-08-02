import json
from math import floor
from typing import List, Optional, TypeVar
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, Request
from fastapi_pagination import Page, Params, add_pagination, paginate
from fastapi_pagination.default import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from fastapi_pagination.links import Page
from movies.api_doc import lst_movie_response
from movies.models import Movie
from movies.schemas import CustomPage, MovieListSchemas
from sqlalchemy import desc

from .database import DB, get_db

app = FastAPI(
    title="Movy API",
    description="""Movy API facilitates movie ticket booking and reservations by providing movie details, showtimes,
                    and reservation management. It supports efficient navigation through movie
                    listings and delivers essential information such as titles, release dates, and posters.""",
    version="1.0.0",
)

T = TypeVar("T")


def get_custom_page(
    page: Page[T], request: Request, params: Params
) -> CustomPage:
    """
    override the default Page fastapi _pagination
    """
    total_pages = (
        page.total if page.total else 0 + params.size - 1
    ) // params.size  # Calculate total pages
    current_page = params.page
    pages_remaining = total_pages - current_page  # Calculate pages remaining

    base_url = str(request.url).split("?")[0]
    query_params = request.query_params

    def create_url(page_num: int) -> str:
        query_params._dict["page"] = page_num
        return f"{base_url}?{urlencode(query_params)}"

    next_url = (
        create_url(current_page + 1) if current_page < total_pages else None
    )
    prev_url = create_url(current_page - 1) if current_page > 1 else None
    return CustomPage(
        results=page.items,
        total=page.total,
        next=next_url,
        prev=prev_url,
        total_pages=total_pages,
        pages_remaining=pages_remaining,
        page_size=page.size,
    )


def default_params() -> Params:
    return Params(size=20)


class CustomParams(Params):
    size: int = 20


@app.get(
    "/",
    response_model=CustomPage[MovieListSchemas],
    status_code=200,
    response_description="endpoint for listing every movies in the database",
    responses=lst_movie_response,
    tags=["MOVY LISTING"]
)
def get_all_movies(
    request: Request,
    db: DB = Depends(get_db),
    params: CustomParams = Depends(),
) -> CustomPage[MovieListSchemas]:

    from main.m_db import REDIS_CLI
    value_set = REDIS_CLI.get("movie_list_value")

    # add the data for caching
    if not value_set:
        movies_query = (
            db._session.query(Movie).order_by(desc(Movie.release_date)).all()
        )
        m_list = [
            MovieListSchemas(
                **{
                    "id": movie.id,
                    "title": movie.title,
                    "tagline": movie.tag_line,
                    "runtime": f"{movie.duration_in_min // 60}hr {movie.duration_in_min % 60}min",
                    "release_date": str(movie.release_date),
                    "poster_path": movie.poster_path,
                    "url": f"{request.base_url}{movie.get_path}",
                }
            )
            for movie in movies_query
        ]
        # fetch the data from caching
        value_set = REDIS_CLI.set(
            "movie_list_value",
            json.dumps([movie.model_dump_json() for movie in m_list]),
        )
    else:
        value_set = REDIS_CLI.get("movie_list_value").decode("UTF-8")
        m_list = [
            MovieListSchemas(**json.loads(movie))
            for movie in json.loads(value_set)
        ]
    default_page = paginate(m_list, params)
    custom_page = get_custom_page(default_page, request, params)

    return custom_page


add_pagination(app)

from movies import movie_routes
from users import user_routes

app.include_router(movie_routes.router)
app.include_router(user_routes.router)
