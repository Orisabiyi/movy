from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Generic, TypeVar, List


class MovieBaseSchema(BaseModel):
    ...


class MovieListSchemas(MovieBaseSchema):
    id: int
    title: str
    tag_line: str
    run_time: str
    release_date: str
    poster_path: str
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