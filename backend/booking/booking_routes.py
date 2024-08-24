from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from main.database import DB, get_db
from main.decorators import PermissionDependency, Role, login_required
from main.hash_id import decode_id, encode_id
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from theatre.models import ShowTime
from theatre.theatre_management.models import Screen, Seat
from users.models import User

from .models import Booking
from .schemas import (
    BookingRequest,
    BookingUpdate,
    UserBookingResponse,
    UserBookingsResponse,
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
        return JSONResponse(
            status_code=400,
            content={"messge": "the chosen seats are already reserved"},
        )
    try:
        booking = Booking(
            showtime_id=decode_id(data.showtime_id), user_id=current_user.id, price=price
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
        content={"message": "Booking successful", "booking_id": booking.id},
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
                    "price": float(booking.price),
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
    booking = db._session.query(Booking).filter(Booking.id == b_id, Booking.user_id == current_user.id).first()

    if not booking:
        return JSONResponse(status_code=404, content={"message": "User booking not found"})
    db._session.delete(booking)
    db._session.commit()
    return JSONResponse(status_code=200, content={"message": "User booking deleted successfully"})

