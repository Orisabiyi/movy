from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing import Optional, Generic, TypeVar, List, Dict



class MovieBaseSchema(BaseModel):
    ...


class MovieListSchemas(MovieBaseSchema):
    id: int
    title: str
    tagline: str
    runtime: str
    release_date: str
    poster_path: str
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
    id: int
    title: str
    description: str
    tag_line: str
    runtime: str
    release_date: str
    trailer_link: Optional[str] = None
    poster_path: str
    backdrop_path: str
    genres: List[str]
    starring: List[Dict[str, str]]
    # movie_production_com: List[str]


class GenreList(BaseModel):
    id: int
    name: str