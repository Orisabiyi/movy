from main.database import Base, get_db
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, func


class Booking(Base):
    __tablename__ = "booking"
    id = Column(Integer, primary_key=True, autoincrement=True)
    