from sqlalchemy import Column, Index, Integer, String, Boolean, Text, Date, DateTime, func
from main.database import Base, DB



class Movie(Base):
    """
    the movie model creation
    """
    __tablename__ = 'movies'
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    genre = Column(String(10), nullable=False)
    rating = Column(String(20), nullable=False)
    language = Column(String(20), nullable=True)
    poster_image = Column(String())
    production_company = Column(String(100), nullable=True)
    trailer_link = Column(String(200), nullable=True)
    duration_in_min = Column(Integer)
    release_year = Column(Date)
    uploaded_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index('ix_title', 'title'),
        Index('ix_release_year', 'release_year'),
        Index('ix_rating', 'rating'),
        Index('ix_genre', 'genre'),
        Index('ix_language', 'language')
    )


class Cast(Base):
    __tablename__ = 'casts'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(50))

    __table_args = (
        Index("ix_name", 'name')
    )

