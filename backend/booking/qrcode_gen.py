import json
from io import BytesIO

from fastapi import HTTPException
import qrcode
import requests
from main.database import DB
from main.hash_id import decode_id, encode_id
from main.util_files import unique_string
from sqlalchemy.exc  import NoResultFound
from sqlalchemy.orm import joinedload
from theatre.models import ShowTime
from theatre.theatre_management.models import Screen, Seat

from .models import Booking, Ticket, booking_seat


class QRCode:
    def __init__(self, data, user_id: int, db: DB):
        self.data = data
        self.user_id = user_id
        self.db = DB()

    def generate_qrcode(self):
        """
        generate user qrcode for the
        """
        booking = (
        self.db._session.query(Booking)
        .filter(Booking.user_id == self.user_id, Booking.id == self.data.booking_id)
        .options(
            joinedload(Booking.show_time)
            .joinedload(ShowTime.screen)
            .joinedload(Screen.theatre),
            joinedload(Booking.show_time).joinedload(ShowTime.movies),
            joinedload(Booking.seats).joinedload(Seat.booking),
        ).first()
    )
        if not booking:
            return HTTPException(status_code=404, detail={"message": "Booking not found"})


    #    ticket = (
           
    #     ) 

        
 