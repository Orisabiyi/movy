from main.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    func,
    Time,
    Date,
    Numeric,
    UniqueConstraint,
)
from users.models import User
import uuid
from sqlalchemy.orm import relationship, backref, mapped_column


theatre_address = Table(
    "theatre_address",
    Base.metadata,
    # Column("id", Integer, primary_key=True, autoincrement=True),
    Column("address_id", ForeignKey("address.id"), primary_key=True),
    Column("theatre_id", ForeignKey("theatre.id"), primary_key=True),
    extend_existing=True,
)

class Theatre(Base):
    __tablename__ = "theatre"
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False, unique=True)
    password = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    role = Column(String(10), default="theatre_owner", nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(50), default="theatre")
    tokens = relationship("TheatreToken", back_populates="theatre")

    @property
    def get_name(self) -> str:
        return f"{self.name}"


    def get_context_string(self, context: str) -> bytes:
        from main import settings
        return f"{context}{self.password[-6]}{self.updated_at.strftime('%m%d%Y%H%M%S')}".encode()

    def __str__(self):
        return self.name

    address = relationship("Address", secondary=theatre_address, back_populates="theatres")

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
    user_id = Column(String(50), ForeignKey("users.id"))
    theatre_id = Column(String(50), ForeignKey("theatre.id"))
    users = relationship(User, backref="reviews")
    theatre = relationship(Theatre, backref="reviews")


class ShowTime(Base):
    __tablename__ = "show_time"
    from .theatre_management.models import Screen
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_movie_time = Column(Time, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    date =  Column(Date, nullable=False)
    price = Column(Numeric(precision=10, scale=2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    screen_id = mapped_column(ForeignKey("screen.id"))
    screen = relationship(Screen, backref="show_times")
    movies = relationship("Movie", back_populates="show_times") 


class TheatreToken(Base):
    __tablename__ = "theatre_token"
    id = Column(Integer, primary_key=True, autoincrement=True)
    theatre_id = mapped_column(ForeignKey("theatre.id"))
    access_token = Column(String(250), nullable=True, index=True, default=None)
    refresh_token = Column(String(250), nullable=True, index=True,  default=None)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    theatre = relationship("Theatre", back_populates="tokens")


