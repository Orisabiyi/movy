import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from .settings import DATABASE_DICT

DATABASE_URL = (
    f'mysql+pymysql://{DATABASE_DICT["USERNAME"]}:'
    + f'{DATABASE_DICT["PASSWORD"]}@{DATABASE_DICT["HOST"]}:'
    + f'{DATABASE_DICT["PORT"]}/{DATABASE_DICT["DATABASE"]}'
)

Base = declarative_base()


class DB:
    def __init__(self):
        from movies.models import Movie
        """
        initalite sql engine and session for sql
        """
        self._engine = create_engine(DATABASE_URL, echo=False)
        self.__session: Session | None = None
        if os.getenv("TEST_DB") == "1":
            Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)

    @property
    def session(self) -> Session:
        """
        create database session for users
        """
        DBsession = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )
        self.__session = DBsession()
        return self.__session

    @property
    def close(self):
        if self.__session:
            self.__session.close()
        self.__session = None
