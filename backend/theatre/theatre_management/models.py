from sqlalchemy import Column, Integer, DateTime, String, func, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import mapped_column, relationship
from theatre.models import Theatre
from main.database import Base

class Screen(Base):
    __tablename__ = "screen"
    id = Column(Integer, primary_key=True, autoincrement=True)
    screen_name = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    theatre_id = mapped_column(ForeignKey("theatre.id"), nullable=False)
    theatre = relationship(Theatre, backref="screen")
    seats = relationship("Seat", back_populates="screen")

    __table_args__ = (UniqueConstraint("screen_name", "theatre_id", name="uniq_theatre_screen_name"),)

class Seat(Base):
    __tablename__ = "seat"
    id = Column(Integer, primary_key=True, autoincrement=True)
    screen_id = mapped_column(ForeignKey("screen.id"), nullable=False)
    row = Column(String(1), nullable=False)
    seat_number = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    screen = relationship("Screen", back_populates="seats")