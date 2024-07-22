import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent

env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

USERNAME = os.getenv("TEST_USERNAME")
DATABASE = os.getenv("TEST_DATABASE")
HOST = os.getenv("TEST_HOST")
PASSWORD = os.getenv("TEST_PASSWORD")

if os.getenv("TEST_DB") != "1":
    USERNAME = os.getenv("USERNAME")
    DATABASE = os.getenv("DATABASE")
    HOST = os.getenv("HOST")
    PASSWORD = os.getenv("PASSWORD")

PORT: int = int(os.getenv("PORT", 3306))
DATABASE_URL = (
    f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)

Base = declarative_base()


class DB:
    def __init__(self):
        """
        initalite sql engine and session for sql
        """
        self._engine = create_engine(DATABASE_URL, echo=False)
        self.__session: Session | None = None
        if os.getenv("TEST_DB") == 1:
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
