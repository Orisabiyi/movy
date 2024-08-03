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
)
from users.models import User
from sqlalchemy.orm import relationship


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
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime)

    def __str__(self):
        return self.name

    theatres = relationship("Address", secondary=theatre_address, back_populates="address")

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
    id = Column(Integer, primary_key=True, autoincrement=True)
    review = Column(Text)
    rating = Column(Integer)
    user_id = Column(Integer, ForeignKey("user.id"))
    theatre_id = Column(Integer, ForeignKey("theatre.id"))

    users = relationship(User, backref="review")
    theatres = relationship(Theatre, backref="theatre")
    
