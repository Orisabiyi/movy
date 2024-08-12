from main.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    func,
    Time,
    Date
)
from users.models import User
from sqlalchemy.orm import relationship, backref


theatre_address = Table(
    "theatre_address",
    Base.metadata,
    # Column("id", Integer, primary_key=True, autoincrement=True),
    Column("address_id", ForeignKey("address.id"), primary_key=True),
    Column("theatre_id", ForeignKey("theatre.id"), primary_key=True)
)

class Theatre(Base):
    __tablename__ = "theatre"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    def __str__(self):
        return self.name

    address = relationship("Address", secondary=theatre_address, back_populates="theatres")
    show_times = relationship("ShowTime", back_populates="theatre") 

class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, autoincrement=True)
    street = Column(String(299))
    city = Column(String(100))
    state = Column(String(100))

    theatres = relationship(Theatre, secondary=theatre_address, back_populates="address")
    def __str__(self):
        return f"{self.street} {self.city} {self.state}"



class TheatreReviewRating(Base):
    __tablename__ = "theatre_review_rating"
    id = Column(Integer, primary_key=True, autoincrement=True)
    review = Column(Text)
    rating = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    theatre_id = Column(Integer, ForeignKey("theatre.id"))
    users = relationship(User, backref="reviews")
    theatre = relationship(Theatre, backref="reviews")


class ShowTime(Base):
    __tablename__ = "show_time"
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(Time, nullable=False)
    date =  Column(Date, nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    theatre_id = Column(Integer, ForeignKey("theatre.id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    theatre = relationship(Theatre, back_populates="show_times") 
    movie = relationship("Movie", back_populates="show_times") 