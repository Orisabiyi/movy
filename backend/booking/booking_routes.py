from datetime import datetime, timedelta

import pyotp
import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from main import settings
from main.database import DB, get_db
from main.decorators import PermissionDependency, Role, login_required
from main.hash_id import decode_id, encode_id
from main.util_files import unique_string
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from theatre.models import ShowTime, Theatre
from theatre.theatre_management.models import Screen, Seat
from users.models import User

from .models import Booking, BookingStatus, Tokens, booking_seat
from .schemas import (
    BookingPayment,
    BookingRequest,
    BookingUpdate,
    BookingVerifyTransaction,
    UserBookingResponse,
    UserBookingsResponse,
    VerifyOtpToken,
)

router = APIRouter(prefix="/booking", tags=["MOVY BOOKING"])


@router.post("/")
@login_required(User)
async def book_movie(
    request: Request,
    data: BookingRequest,
    db: DB = Depends(get_db),
    current_user=Depends(PermissionDependency(Role.USER, User)),
):
    """
    create user booking
    """
    print("---------------------> hwere ")
    show_time = (
        db._session.query(ShowTime)
        .filter(ShowTime.id == decode_id(data.showtime_id))
        .first()
    )

    if not show_time:
        return JSONResponse(
            status_code=404, content={"message": "Show Time not found"}
        )
    seat_ids = [decode_id(seat.seat_id) for seat in data.seats]
    price = 0
    for seat in seat_ids:
        price += show_time.price
    seat_available = (
        db._session.query(Seat)
        .filter(Seat.id.in_(seat_ids), Seat.is_available == True)
        .all()
    )
    if len(seat_available) != len(seat_ids):
        print(len(seat_available))
        return JSONResponse(
            status_code=400,
            content={"messge": "the chosen seats are already reserved"},
        )
    try:
        booking = Booking(
            showtime_id=decode_id(data.showtime_id),
            user_id=current_user.id,
            price=price,
        )
        db._session.add(booking)
        db._session.commit()
        db._session.refresh(booking)
    except IntegrityError:
        return JSONResponse(
            status_code=400,
            content={"messsage": "You can only book movie once"},
        )

    for seat in seat_available:
        seat.is_available = False  # type: ignore
        booking.seats.append(seat)
        db._session.commit()

    return JSONResponse(
        status_code=201,
        content={"message": "Booking successful", "booking_id": encode_id(booking.id)},  # type: ignore
    )


@router.get("/", response_model=UserBookingsResponse)
@login_required(User)
async def get_user_bookings(
    request: Request,
    db: DB = Depends(get_db),
    current_user=Depends(PermissionDependency(Role.USER, User)),
):
    """
    get all user booking from db
    """
    bookings = (
        db._session.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .options(
            joinedload(Booking.show_time)
            .joinedload(ShowTime.screen)
            .joinedload(Screen.theatre),
            joinedload(Booking.show_time).joinedload(ShowTime.movies),
            # joinedload(Booking.seats).joinedload(BookingSeat.seat),
        )
        .all()
    )

    if not bookings:
        raise HTTPException(
            status_code=404, detail="No bookings found for this user"
        )

    bookings_response = UserBookingsResponse(
        user_id=current_user.id,
        bookings=[
            UserBookingResponse(
                booking_id=encode_id(booking.id),  # type: ignore
                status=booking.status,  # type: ignore
                movie={
                    "movie_id": encode_id(booking.show_time.movies.id),
                    "title": booking.show_time.movies.title,
                },
                theatre={
                    "theatre_id": booking.show_time.screen.theatre.id,
                    "theatre_name": booking.show_time.screen.theatre.name,
                },
                screen={
                    "screen_id": encode_id(booking.show_time.screen.id),
                    "screen_name": booking.show_time.screen.screen_name,
                },
                showtime={
                    "showtime_id": encode_id(booking.show_time.id),
                    "date": booking.show_time.date.strftime("%Y-%m-%d"),
                    "movie_start_time": booking.show_time.start_movie_time.strftime(
                        "%H:%M"
                    ),
                    "price": float(booking.price),  # type: ignore
                },
                seats=[
                    {
                        "seat_id": encode_id(seat.id),
                        "row": seat.row,
                        "seat_number": seat.seat_number,
                    }
                    for seat in booking.seats
                ],
            )
            for booking in bookings
        ],
    )
    data = bookings_response.model_dump()
    # data["bookings"] = bookings_response.model_dump()["bookings"]
    return JSONResponse(content=data, status_code=200)


@router.patch("/{booking_id}/update-seats")
@login_required(User)
async def update_user_booking(
    request: Request,
    data: BookingUpdate,
    booking_id: str,
    db: DB = Depends(get_db),
    current_user=Depends(PermissionDependency(Role.USER, User)),
):
    """
    update user seat boooking
    """
    b_id = decode_id(booking_id)
    booking = (
        db._session.query(Booking)
        .filter(Booking.id == b_id, Booking.user_id == current_user.id)
        .first()
    )
    if not booking:
        return JSONResponse(
            status_code=401, content={"message": "Booking id not found"}
        )

    seats = [decode_id(seat) for seat in data.seats]
    request_seats = db._session.query(Seat).filter(Seat.id.in_(seats))

    if not request_seats:
        return JSONResponse(
            status_code=404, content={"message": "Seats not found"}
        )

    current_seats = {seat.id for seat in booking.seats}
    req_seats_id = {seat.id for seat in request_seats}
    seat_to_add = req_seats_id - current_seats
    seat_to_remove = current_seats - req_seats_id

    # check seat availability
    seat_available = (
        db._session.query(Seat)
        .filter(Seat.id.in_(seat_to_add), Seat.is_available == False)
        .all()
    )
    if seat_available:
        return JSONResponse(
            status_code=400,
            content={"message": "One or more seats are already booked"},
        )

    # deduct user booked seats
    for seat in seat_to_remove:
        instance = db._session.query(Seat).filter(Seat.id == seat).first()
        if instance:
            instance.is_available = True  # type: ignore
            booking.seats.remove(instance)
            db._session.commit()

    # Add to user seats
    for seat in seat_to_add:
        seat_instance = db._session.query(Seat).filter(Seat.id == seat).first()
        seat_instance.is_available = False  # type: ignore
        booking.seats.append(seat_instance)

    db._session.commit()
    db._session.refresh(booking)

    return JSONResponse(
        content={"message": "User booking updated", "id": booking.id},
        status_code=200,
    )


@router.delete("/{booking_id}/cancel-booking")
@login_required(User)
async def delete_user_booking(
    request: Request,
    booking_id: str,
    db: DB = Depends(get_db),
    current_user=Depends(PermissionDependency(Role.USER, User)),
):
    """
    delete user booking
    """
    b_id = decode_id(booking_id)
    booking = (
        db._session.query(Booking)
        .filter(Booking.id == b_id, Booking.user_id == current_user.id)
        .first()
    )

    if not booking:
        return JSONResponse(
            status_code=404, content={"message": "User booking not found"}
        )
    db._session.delete(booking)
    db._session.commit()
    return JSONResponse(
        status_code=200,
        content={"message": "User booking deleted successfully"},
    )


@router.post("/payment")
@login_required(User)
async def make_payment(
    request: Request,
    data: BookingPayment,
    db: DB = Depends(get_db),
    current_user=Depends(PermissionDependency(Role.USER, User)),
):
    booking_id = decode_id(data.booking_id)
    booked = (
        db._session.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == current_user.id)
        .first()
    )
    if not booked:
        return JSONResponse(
            content={"message": "Booking not Found"}, status_code=400
        )

    # send user payment to paystack API
    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}", "Content-Type": "application/json"}  # type: ignore
    post_data = {
        "email": current_user.email,
        "amount": int(booked.price) * 100,  # type: ignore
        "currency": "NGN",
    }
    resp = requests.post(url=url, headers=headers, json=post_data)

    if resp.status_code != 200:
        print(resp.json())
        return JSONResponse(status_code=400, content=resp.json())

    return JSONResponse(status_code=200, content=resp.json())


@router.post("/verify-payment")
@login_required(User)
async def verify_user_booking_payment(
    request: Request,
    data: BookingVerifyTransaction,
    db: DB = Depends(get_db),
    current_user=Depends(PermissionDependency(Role.USER, User)),
):
    book_id = decode_id(data.booking_id)

    booking = (
        db._session.query(Booking)
        .filter(Booking.id == book_id, Booking.user_id == current_user.id)
        .options(
            joinedload(Booking.show_time)
            .joinedload(ShowTime.screen)
            .joinedload(Screen.theatre),
            joinedload(Booking.show_time).joinedload(ShowTime.movies),
            # joinedload(Booking.seats).joinedload(BookingSeat.seat),
        )
        .first()
    )

    url = f"https://api.paystack.co/transaction/verify/{data.reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}  # type: ignore

    resp = requests.get(url=url, headers=headers)
    try:
        response = resp.json()
        if response["data"]["status"] != "success":
            return JSONResponse(
                content="Unsuccessful transaction", status_code=400
            )
    except (requests.RequestException, requests.ReadTimeout) as e:
        return JSONResponse(f"Network error: {e}", status_code=500)

    if not booking:
        return JSONResponse(
            status_code=404, content={"message": "Booking for user not found"}
        )
    booking.status = BookingStatus.CONFIRMED  # type: ignore
    db._session.commit()

    # generate user token key
    totp = pyotp.TOTP("base32secret3232")
    token = Tokens(
        otp_code=int(totp.now()),
        booking_id=booking.id,
        user_id=current_user.id,
        theatre_id=booking.show_time.screen.theatre.id,
        expires_at=booking.show_time.expires_at + timedelta(hours=30),
    )
    db._session.add(token)
    db._session.commit()
    db._session.refresh(token)
    token_dict = {
        "otp_code": token.otp_code,
        "expirest_at": token.expires_at.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    return JSONResponse(status_code=200, content=token_dict)



@router.post("/verify-booking", tags=["Theare Verify Booking"])
@login_required(Theatre)
async def verify_uuser_provided_token(
    request: Request,
    data: VerifyOtpToken,
    db: DB = Depends(get_db),
    thea=Depends(PermissionDependency(Role.THEATRE, Theatre)),
):
    token = db._session.query(Tokens).filter(Tokens.otp_code == data.code, Tokens.theatre_id == thea.id).first()

    # booked = db._session.query(Booking).
    if not token:
        return JSONResponse(content={"message": "Invalid token provided"}, status_code=400)
    booking = (
        db._session.query(Booking)
        .filter(Booking.id == token.booking_id)
        .options(
            joinedload(Booking.show_time)
            .joinedload(ShowTime.screen)
            .joinedload(Screen.theatre),
            joinedload(Booking.show_time).joinedload(ShowTime.movies),
            # joinedload(Booking.seats).joinedload(BookingSeat.seat),
        )
        .first()
    )

    if not booking:
        return JSONResponse(content={"Vmessage": "Invalid token provided"}, status_code=400)


    if token.expires_at < datetime.now(): #type: ignore
        booking.status = BookingStatus.CANCELED #type: ignore
        for seat in booking.seats:
            seat.is_available=True
            db._session.commit()
        return JSONResponse(content={"message": "Token expired"}, status_code=400)

    for seat in booking.seats:
        seat.is_available = True
        db._session.commit()
    booking_info = {
        "viewer": token.user.get_name,
        "theatre_name": booking.show_time.screen.theatre.name,
        "movie_title": booking.show_time.movies.title,
        "screen_name": booking.show_time.screen.screen_name,
        "seats": [f"{seat.row}{seat.seat_number}" for seat in booking.seats],
        "booking_status": booking.status.value,
        "expires_at": token.expires_at.strftime("%Y-%m-%dT:%H:%M:%S")
    }
    return JSONResponse(content=booking_info, status_code=200)