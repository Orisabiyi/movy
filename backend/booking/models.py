import enum
from main.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    Table,
    UniqueConstraint,
    Numeric,
)
from sqlalchemy.orm import mapped_column, relationship


class BookingStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELED = "canceled"


booking_seat = Table (
    "booking_seat", Base.metadata,
    Column("id", Integer, primary_key=True,  autoincrement=True),
    Column("seat_id", Integer, ForeignKey("seat.id")),
    Column("booking_id", Integer, ForeignKey("bookings.id"))
)

ticket_seat = Table (
    "ticket_seat", Base.metadata,
    Column("id", Integer, primary_key=True,  autoincrement=True),
    Column("ticket_id", Integer, ForeignKey("ticket.id")),
    Column("seat_id", Integer, ForeignKey("seat.id"))
)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(20), default="pending")
    price  =  Column(Numeric(precision=10, scale=2), nullable=False)
    booking_time = Column(DateTime, server_default=func.now())
    theatre_id = mapped_column(ForeignKey("theatre.id"))
    updated_at = Column(DateTime, onupdate=func.now())
    user_id = mapped_column(ForeignKey("users.id"))
    showtime_id  = mapped_column(ForeignKey("show_time.id"), nullable=False)
    seats = relationship("Seat", secondary=booking_seat,back_populates="booking")
    user = relationship("User", backref="user_booking")
    show_time = relationship("ShowTime", backref="showtime_booking")
    theatre = relationship("Theatre", backref="booking")

    __table_args__ = (UniqueConstraint("showtime_id", "user_id", name="uniq_user_showtime"),)


class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_number = Column(String(200), unique=True, nullable=False)  # Unique ticket number or ID
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    user_id = Column(String(100), ForeignKey("users.id"), nullable=False)
    theatre_id = Column(String(100), ForeignKey("theatre.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)  # Added movie_id
    seat_id = Column(Integer, ForeignKey("seat.id"), nullable=False)
    screen_id = Column(Integer, ForeignKey("screen.id"), nullable=False)
    issued_at = Column(DateTime, server_default=func.now(), nullable=False)  # When the ticket was issued
    expires_at = Column(DateTime, nullable=False)
    qr_code_path = Column(String(500), nullable=True)  # Path to a QR code for the ticket (if applicable)
 
    # Relationships
    booking = relationship("Booking", backref="tickets")
    user = relationship("User", backref="tickets")
    seat = relationship("Seat",secondary=ticket_seat, backref="tickets")
    movie = relationship("Movie", backref="tickets")
    screen = relationship("Screen", backref="tickets")

