from datetime import datetime
import json
from typing import List, Optional, TypeVar

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_pagination import add_pagination, paginate
from movies.api_doc import lst_movie_response
from movies.models import Movie
from movies.schemas import CustomPage, MovieListSchemas
from sqlalchemy import desc

from .database import DB, get_db
from .pagination import CustomPage, CustomParams, get_custom_page
from .util_files import movie_schema_list

app = FastAPI(
    title="Movy API",
    description="""Movy API facilitates movie ticket booking and reservations by providing movie details, showtimes,
                    and reservation management. It supports efficient navigation through movie
                    listings and delivers essential information such as titles, release dates, and posters.""",
    version="1.0",
)


# middleware setup
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    response_model=CustomPage[MovieListSchemas],
    status_code=200,
    response_description="endpoint for listing every movies in the database",
    responses=lst_movie_response,  # type: ignore
    tags=["MOVY LISTING"],
)
def get_all_movies(
    request: Request,
    db: DB = Depends(get_db),
    params: CustomParams = Depends(),
) -> CustomPage[MovieListSchemas]:

    from main.m_db import REDIS_CLI

    all_movies = REDIS_CLI.get("movie_list_value")

    # add the data for caching
    if not all_movies:
        movies_query = (
            db._session.query(Movie).filter(Movie.release_date < datetime.now()).order_by(desc(Movie.release_date)).all()
        )
        m_list = movie_schema_list(request, movies_query)
        # fetch the data from caching
        value_set = REDIS_CLI.set(
            "movie_list_value",
            json.dumps([movie.model_dump_json() for movie in m_list]),
        )
    else:
        value_set = all_movies.decode("UTF-8")  # type: ignore
        m_list = [
            MovieListSchemas(**json.loads(movie))
            for movie in json.loads(value_set)
        ]
    default_page = paginate(m_list, params)
    custom_page = get_custom_page(default_page, request, params)

    return custom_page


@app.get('/upcoming-movies', response_model=List[MovieListSchemas], status_code=200)
def get_upcoming_movies(request: Request, db: DB = Depends(get_db)):
    """
    return list of all upcoming movies
    """
    today = datetime.now().date()
    movies = db._session.query(Movie).filter(Movie.release_date > today).all()

    if not movies:
        return JSONResponse(status_code=400, content={"message": "No upcomig movies"})


    m_list = movie_schema_list(request, movies)
    return m_list
 

add_pagination(app)

from booking import booking_routes
from movies import movie_routes
from theatre import theater_routes
from theatre.theatre_management import showtime_routers
from users import user_routes

app.include_router(movie_routes.router)
app.include_router(user_routes.router)
app.include_router(theater_routes.router)
app.include_router(showtime_routers.router)
app.include_router(booking_routes.router)


async def custom_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    errors = exc.errors()
    # Customize the format here
    custom_errors = [
        {
            "field": error["loc"][1],
            "message": error["msg"],
            "error_type": error["type"],
        }
        for error in errors
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"errors": custom_errors},
    )


app.add_exception_handler(
    RequestValidationError, custom_validation_exception_handler  # type: ignore
)

from fastapi.openapi.utils import get_openapi


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Movy Booking API",
        version="1.0",
        description="This is the documentation for the MOVY booking API",
        routes=app.routes,
    )

    validation_error_schema = {
        "type": "object",
        "properties": {
            "errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "field": {"type": "string"},
                        "message": {"type": "string"},
                        "error_type": {"type": "string"},
                    },
                },
            }
        },
    }

    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if "422" in openapi_schema["paths"][path][method]["responses"]:
                openapi_schema["paths"][path][method]["responses"]["422"] = {
                    "description": "Validation Error",
                    "content": {
                        "application/json": {"schema": validation_error_schema}
                    },
                }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
