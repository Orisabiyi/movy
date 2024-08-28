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
    def __init__(self, data, db: DB):
        self.db = DB()
        self.data = data

    def generate_qrcode(self):
        """
        generate user qrcode for the
        """