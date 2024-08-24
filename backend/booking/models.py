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
class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(20), default="pending")
    booking_time = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    user_id = mapped_column(ForeignKey("users.id"))
    showtime_id  = mapped_column(ForeignKey("show_time.id"), nullable=False)
    seats = relationship("Seat", secondary=booking_seat,back_populates="booking")
    user = relationship("User", backref="user_booking")
    show_time = relationship("ShowTime", backref="showtime_booking")

    __table_args__ = (UniqueConstraint("showtime_id", "user_id", name="uniq_user_showtime"),)


class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(Integer, primary_key=True, autoincrement=True)
     