"""
calculate seats and rows
"""
from .models import Seat


def generate_seats(screen, rows, seats_per_row):
    seat_data = []
    for row in range(rows):
        row_label = chr(65 + row)  # Converts 0 -> A, 1 -> B, etc.
        for seat_number in range(1, seats_per_row + 1):
            seat = Seat(
                row=row_label,
                seat_number=seat_number,
                screen=screen
            )
            seat_data.append(seat)
    return seat_data
