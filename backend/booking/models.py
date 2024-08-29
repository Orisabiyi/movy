import enum

from main.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import mapped_column, relationship


class BookingStatus(enum.Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELED = "Canceled"


booking_seat = Table(
    "booking_seat",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("seat_id", Integer, ForeignKey("seat.id")),
    Column("booking_id", Integer, ForeignKey("bookings.id")),
)



class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(
        Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False
    )
    price = Column(Numeric(precision=10, scale=2), nullable=False)
    booking_time = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    user_id = mapped_column(ForeignKey("users.id"))

    showtime_id = mapped_column(ForeignKey("show_time.id"), nullable=False)
    seats = relationship(
        "Seat", secondary=booking_seat, back_populates="booking"
    )
    user = relationship("User", backref="user_booking")
    show_time = relationship("ShowTime", backref="showtime_booking")

    __table_args__ = (
        UniqueConstraint("showtime_id", "user_id", name="uniq_user_showtime"),
    )

class Tokens(Base):
    __tablename__ = "token"
    id = Column(Integer, primary_key=True, autoincrement=True)
    otp_code = Column(Integer, unique=True, nullable=True)
    booking_id = mapped_column(ForeignKey("bookings.id"))
    user_id = mapped_column(ForeignKey("users.id"))
    theatre_id = mapped_column(ForeignKey("theatre.id"))
    expires_at = Column(DateTime)

    user = relationship("User", backref="otp_tokens")
    booking = relationship("Booking", backref="booking")
    theatre = relationship("Theatre", backref="booking")