import enum

from main.database import DB, Base
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
    Column("movie_id", ForeignKey("movies.id")),
    Column("cast_id", ForeignKey("casts.id")),
)

# Association table for many-to-many relationship between movies and genre
movie_genre_association = Table(
    "movie_genre",
    Base.metadata,
    Column("movie_id", Integer, ForeignKey("movies.id")),
    Column("genre_id", Integer, ForeignKey("genres.id")),
)

# Association table for many-to-many relationship between production company and movie
movie_production_company = Table(
    "movie_production_company",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id")),
    Column("production_company_id", ForeignKey("production_company.id")),
)


class Movie(Base):
    """
    the movie model creation
    """

    __tablename__ = "movies"
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

    # primary_lang_id = Column(
    #     Integer, ForeignKey("language.id"), nullable=True
    # )
    # primary_language = relationship("Language", uselist=False, backref="movie")

    movie_production_com = relationship(
        "ProductionCompany",
        secondary=movie_production_company,
        back_populates="production_com_movies",
    )
    movie_casts = relationship(
        "Cast", secondary=movie_cast, back_populates="casts_movie"
    )
    movie_genres = relationship(
        "Genre",
        secondary=movie_genre_association,
        back_populates="genre_movies",
    )

    __table_args__ = (
        Index("ix_title", "title"),
        Index("ix_release_date", "release_date"),
    )

    def __str__(self):
        return self.title

    @property
    def get_path(self):
        return f'/movies/{self.id}'

    def movie_to_dict(self):
        dct = self.__dict__
        del dct["_sa_instance_state"]
        del dct["uploaded_at"]
        dct = {
            "id": dct["id"],
            "title": dct["title"],
            "description": dct["description"],
            "poster_path": dct["poster_path"],
            "backdrop_path": dct["backdrop_path"],
            "tag_line": dct["tag_line"],
            "trailer_link": dct["trailer_link"],
            "runtime": f"{dct['duration_in_min']// 60}hr {dct['duration_in_min'] % 60}min",
            "release_date": str(dct["release_date"]),
            "genres": [genre.name for genre in dct["movie_genres"]],
            "starring": [
                {"name": cast.name, "profile_path": cast.profile_path}
                for cast in dct["movie_casts"]
            ][:10],
        }
        print(dct)
        return dct


# class MovieStatusEnum(enum.Enum):
#     RELEASED= 'Released'
#     UPCOMING = 'Upcoming'


# class MovieStatus(Base):
#     __tablename__ = "movie_status"
#     status = Column()

# class Gender(Base):
#     __tablename__ = "gender"
#     id = Column(Integer, autoincrement=True, primary_key=True, index=True)
#     name = Column(String(6))

#     def __str__(self):
#         return self.name


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


# movie metadata
class Language(Base):
    __tablename__ = "language"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    lang = Column(String(100))

    __table_args = Index("ix_primary_lang", "lang")

    def __str__(self):
        return self.lang


class Genre(Base):
    __tablename__ = "genres"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(20))

    genre_movies = relationship(
        "Movie",
        secondary=movie_genre_association,
        back_populates="movie_genres",
    )
    __table_args = Index("ix_genre_name", "name")

    def __str__(self):
        return self.name


# class MovieCertificationEnum(enum.Enum):
#     NotRated = "NR"
#     General = "G"
#     PG = "PG"
#     PG_13 = "PG-13"
#     R = "R"

#     @classmethod
#     def get_description(cls, certification):
#         descriptions = {
#             cls.NotRated: "Not rated",
#             cls.General: "General",
#             cls.PG: "Parental Guidance",
#             cls.PG_13: "Parents Strongly Cautioned 13+",
#             cls.R: "Restricted 18+",
#         }
#         return descriptions.get(certification, "Unknown rating")


# class MovieCertification(Base):
#     __tablename__ = "certification"
#     id = Column(Integer, primary_key=True, autoincrement=True, index=True)
#     cert = Column(
#         Enum(MovieCertificationEnum), default=MovieCertificationEnum.NotRated
#     )

#     def __str__(self):
#         return self.cert


class Country(Base):
    __tablename__ = "country"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100))

    __table_args = Index("ix_country", "name")

    def __str__(self):
        return self.name


class ProductionCompany(Base):
    __tablename__ = "production_company"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(100))
    production_com_movies = relationship(
        "Movie",
        secondary=movie_production_company,
        back_populates="movie_production_com",
    )
    __table_args = Index("ix_production_company", "name")

    def __str__(self):
        return self.name
