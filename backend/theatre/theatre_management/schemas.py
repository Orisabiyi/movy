from pydantic import BaseModel



class CreateScreen(BaseModel):
    screen_name: str
    capacity: int


class CreateShow(BaseModel):
    screen_name: str
    capacity: int
    total_row_number: int
    total_seat_number: int
    