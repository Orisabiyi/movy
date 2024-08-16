import enum

from backend.main.database import DB, Base
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
from sqlalchemy.orm import relationship

# Association table for many-to-many relationship between movies and cast
movie_cast = Table(
    "movie_cast",
    Base.metadata,
    Column("id", Integer, autoincrement=True, primary_key=True),
    Column("movie_id", ForeignKey("movies.id")),
    Column("cast_id", ForeignKey("casts.id")),
)

# Association table for many-to-many relationship between movies and genre
movie_genre = Table(
    "movie_genre",
    Base.metadata,
    Column("id", Integer, autoincrement=True, primary_key=True),
    Column("movie_id", Integer, ForeignKey("movies.id")),
    Column("genre_id", Integer, ForeignKey("genres.id")),
)


class Movie(Base):
    """
    the movie model creation
    """

    __tablename__ = "movies"
    from theatre.models import ShowTime
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    poster_path = Column(String(200))
    backdrop_path = Column(String(200))
    trailer_link = Column(String(200), nullable=True)
    tag_line = Column(Text, nullable=True)
    duration_in_min = Column(Integer, nullable=True)
    release_date = Column(Date)
    uploaded_at = Column(DateTime, default=func.now())

    show_times = relationship(ShowTime, back_populates="movies")
    movie_casts = relationship(
        "Cast", secondary=movie_cast, back_populates="casts_movie"
    )
    movie_genres = relationship(
        "Genre",
        secondary=movie_genre,
        back_populates="genre_movies",
    )

    def __str__(self):
        return self.title

    @property
    def get_path(self):
        return f"movies/{self.id}"


    __table_args__ = (
        Index(
            "ix_my_table_title_description",
            "title",
            "description",
            "tag_line",
            mysql_prefix="FULLTEXT",
        ),
    )


class Cast(Base):
    """
    cast model movies
    """

    __tablename__ = "casts"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100))
    profile_path = Column(String(100), nullable=True)
    popularity = Column(Float)
    # gender_id = Column(Integer, ForeignKey("gender.id"))
    casts_movie = relationship(
        "Movie", secondary=movie_cast, back_populates="movie_casts"
    )
    # cast_gender = relationship("Gender", backref="gender")
    __table_args = Index("ix_name", "name")

    def __str__(self):
        return self.name


# class MovieRatingReview(Base):
#     id = Column(Integer, autoincrement=True, primary_key=True, index=True)
#     review = Column(Text)
#     rating = Column(Integer)
#     user_id = Column(Integer, ForeignKey("user.id"))
#     movie_id = Column(Integer, ForeignKey("movies.id"))


# class  MovieSchedule(Base):
#     id = Column(Integer, autoincrement=True, primary_key=True, index=True)
#     created_at = Column(DateTime, default=func.now())
#     updated_at = Column(DateTime)
#     movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
#     user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
#     seat_id = Column(Integer, ForeignKey("seat.id"), nullable=False)
#     price = Column()


class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(20))

    genre_movies = relationship(
        "Movie",
        secondary=movie_genre,
        back_populates="movie_genres",
    )
    __table_args = Index("ix_genre_name", "name", mysql_prefix="FULLTEXT")

    def __str__(self):
        return self.name
