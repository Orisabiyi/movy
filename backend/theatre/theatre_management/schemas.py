from typing import Union
from pydantic import BaseModel, field_validator, Field
from decimal import Decimal
from datetime import date, datetime
from datetime import time

# class CreateScreen(BaseModel):
#     screen_name: str
#     capacity: int


class CreateShow(BaseModel):
    movie_id: int
    screen_name: str
    ticket_price: Decimal = Field(..., gt=0, decimal_places=2)
    total_row_number: int
    total_seat_number_in_a_row: int
    movie_date: date
    movie_time_start: time
    ticket_expires_at: datetime

    @field_validator('movie_time_start')
    def parse_time(cls, value: Union[str, time]):
        # Convert string to time object if necessary
        if isinstance(value, str):
            return datetime.strptime(value, "%H:%M").time()
        return value

    # @field_validator("screen_name")
    # def unique_screen_name(cls, vallue):
    #     ...


class MovieList(BaseModel):
    id: int
    title: str

# class MovieListResponse(BaseModel):