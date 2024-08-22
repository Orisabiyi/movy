from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing import Optional, Generic, TypeVar, List, Dict, Union
from datetime import time, date



class MovieBaseSchema(BaseModel):
    ...


class MovieListSchemas(MovieBaseSchema):
    id: str
    title: str
    tagline: str
    runtime: str
    release_date: str
    poster_path: str
    description: str
    url: str
    class config:
        from_attributes = True


T = TypeVar('T')

class CustomPage(BaseModel, Generic[T]):
    total: Optional[int] = Field(default=0)
    next: Optional[str]
    prev: Optional[str]
    total_pages: int
    pages_remaining: int
    page_size: int
    results: List[T]

    class Config:
        from_attributes = True



class MovieDetailSchema(BaseModel):
    id: str
    title: str
    description: str
    tag_line: str
    runtime: str
    release_date: str
    trailer_link: Optional[str] = None
    poster_path: str
    backdrop_path: str
    genres: List[str]
    starring: List[Dict[str, Optional[str]]]


class GenreList(BaseModel):
    id: int
    name: str

class SeatResponse(BaseModel):
    id: int
    row: str
    seat_number: int
    is_available: bool

    class Config:
        from_attributes = True


class ShowTimeSchema(BaseModel):
    showtime_id: int
    date: date
    movie_start_time: time
    movie_end_time: time
    price: float

    class config:
        from_attributes = True

class ScreenSchema(BaseModel):
    screen_id: int
    screen_name: str
    seats: List[SeatResponse]
    showtimes: List[ShowTimeSchema]

    class config:
        from_attributes = True

class TheatreSchema(BaseModel):
    theatre_id: str
    theatre_name: str
    screens: List[ScreenSchema]

    class config:
        from_attributes = True

class MovieTheatreSchema(BaseModel):
    movie_id: str
    title: str
    theatres: List[TheatreSchema]

    class config:
        from_attributes = True
