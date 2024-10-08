from datetime import datetime
from dotenv import find_dotenv, load_dotenv

import pytest

@pytest.fixture(scope='session', autouse=True)
def load_env():
    env_file = find_dotenv('.env.tests')
    load_dotenv(env_file)


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from main.database import Base, get_db
from main.app import app
from fastapi.testclient import TestClient
# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, )
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
import faker


faker = faker.Faker()
EMAIL = faker.email(safe=True, domain="gmail.com")
PASSWORD = faker.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
LAST_NAME = faker.last_name()
FIRST_NAME = faker.first_name()


# Override the get_db dependency
# @pytest.fixture(scope="function")
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    except IntegrityError:
        db.rollback()
        raise 
    finally:
        db.close()
# Create the FastAPI test client
override_app = TestClient(app)
import os

@pytest.fixture(scope="function")
def data():
    return {
        "first_name": FIRST_NAME,
        "last_name": LAST_NAME,
        "email": EMAIL,
        "password": "Batman123!!",
    }


@pytest.fixture(scope="function")
def user(data):
    from users.models import User
    with TestingSessionLocal() as session:
        try:
            user = User(**data)
            user.updated_at = datetime.now() #type: ignore
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except IntegrityError:
            session.rollback()
            return user
         


@pytest.fixture(scope="module")
def db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal
    # Drop the tables after tests are done
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(db):
    app.dependency_overrides[get_db] = override_get_db
    yield override_app
