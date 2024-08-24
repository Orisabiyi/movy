from datetime import date, datetime, time
from typing import Any, Dict, List, Union

from pydantic import BaseModel




class BookingSeat(BaseModel):
    seat_id: str


class BookingRequest(BaseModel):
    showtime_id: str
    seats: List[BookingSeat]

    class Config:
        json_extra_schema = {
            "example": {
                "user_id": 123,
                "showtime_id": 456,
                "seats": [
                    {"seat_id": 1},
                    {"seat_id": 2},
                    {"seat_id": 3},
                ],
            }
        }


class UserBookingResponse(BaseModel):
    booking_id: str
    # booking_time: datetime
    status: str
    movie: Dict[str, Union[int, str, float]]
    theatre: Dict[str, Union[int, str, float]]
    screen: Dict[str, Union[int, str, float]]
    showtime: Dict[str, Union[int, str, float, time, date]]
    seats: List[Dict[str, Union[int, str, float]]]

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.strftime("%Y-%m-%d"),
            time: lambda v: v.strftime("%H:%M"),
        }

class UserBookingsResponse(BaseModel):
    user_id: str
    bookings: List[UserBookingResponse]

    class Config:
        from_attributes = True

class BookingUpdate(BaseModel):
    seats: List[str]