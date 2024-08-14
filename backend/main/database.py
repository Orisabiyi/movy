import os
from typing import Dict, Union

from sqlalchemy import create_engine
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from .settings import BASE_DIR, DATABASE_DICT, DEBUG

DATABASE_URL = (
    f'mysql+pymysql://{DATABASE_DICT["USERNAME"]}:'
    + f'{DATABASE_DICT["PASSWORD"]}@{DATABASE_DICT["HOST"]}:'
    + f'{DATABASE_DICT["PORT"]}/{DATABASE_DICT["DATABASE"]}'
)

Base = declarative_base()

ssl_args = {
    "ssl": {
        "sslmode": "REQUIRED",
        "ca": BASE_DIR / "main" / "ca.pem",
    }
}


class DB:
    def __init__(self):
        from movies.models import Movie

        """
        initalize sql engine and session for sql
        """
        if DEBUG:
            self._engine = create_engine(DATABASE_URL, echo=False)
        else:
            self._engine = create_engine(
                DATABASE_URL, echo=False, connect_args=ssl_args
            )
        # unittest database
        if os.getenv("PYTEST") == "1":
            self._engine = create_engine(os.getenv("DATABASE_URL", ''), echo=False)
        self.__session: Session | None = None
        # if os.getenv("TEST_DB") != "1":
        #     Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)

    @property
    def _session(self) -> Session:
        """
        create database session for users
        """
        if self.__session is None:
            DBsession = sessionmaker(
                autocommit=False, autoflush=False, bind=self._engine
            )
            self.__session = DBsession()
        return self.__session

    @property
    def _close(self):
        if self.__session:
            self.__session.close()
        self.__session = None

    def get_or_add(self, klass, close=True, **kwargs):
        """
        check if a value exist if not add too the value
        """
        instance = None
        try:
            instance = self._session.query(klass).filter_by(**kwargs).one()
        except NoResultFound:
            instance = klass(**kwargs)
            self._session.add(instance)
            self._session.commit()
            self._session.refresh(instance)
            if close:
                self._close
        except MultipleResultsFound:
            instance = self._session.query(klass).filter_by(**kwargs).first()
        return instance

    def add(self, klass, close=True, **kwargs):
        """
        add to the database db
        """
        instance = klass(**kwargs)
        self._session.add(instance)
        self._session.commit()
        self._session.refresh(instance)
        if close:
            self._close
        return instance

    def get(self, klass, **kwargs):
        """
        get instance model
        """
        try:
            instance = self._session.query(klass).filter_by(**kwargs).one()
        except NoResultFound:
            raise NoResultFound(f"Could not find query object {kwargs.keys()}")
        except MultipleResultsFound:
            raise MultipleResultsFound(f"Multiple Results found for get")

        return instance

    def list_all(self, klass, **kwargs):
        """
        return a list of all object in sql
        """
        instance = self._session.query(klass).filter_by(**kwargs)
        return instance


def get_db():
    db = DB()
    try:
        yield db
    finally:
        db._close
