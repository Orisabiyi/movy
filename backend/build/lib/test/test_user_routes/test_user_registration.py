"""
- TEST user was created successfully
- TEST the a validation error is thrown if user input was incorrect
- TEST if the user already exists
"""
import os
from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from test.conftest import FIRST_NAME, LAST_NAME, TestingSessionLocal
from users import models
import pytest



# this test was written to debug the database insertion
# can be commented out if you wants
def test_direct_db_insertion():
    with TestingSessionLocal() as session:
        try:
            user_data = {
                "first_name": FIRST_NAME,
                "last_name": LAST_NAME,
                "email": "kelanisimi@abc.com",
                "password": "Batman123!!",
            }
            db_user = models.User(**user_data)
            session.add(db_user)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise
        assert db_user.first_name == FIRST_NAME #type: ignore


def test_create_user(client, data):
    with TestingSessionLocal() as session:
        try:
            response = client.post(
                "/auth/signup",
                json=data
            )
            assert response.status_code == 201
            assert response.json() == {"message": "User created successfully", "status_code": 201}
        except IntegrityError:
            session.rollback()
            raise
    


def test_invalid_email(client, data):
    data["email"] = "string@string1.com"
    resp = client.post("/auth/signup", json=data)
    assert resp.status_code == 422
    error_msg = {
        "errors": [
            {
                "field": "email",
                "message": "Invalid email address provided",
                "error_type": "string",
            }
        ]
    }
    assert resp.json() == error_msg


def test_invalid_password_too_short(client, data):
    data["password"] = "as3A!"
    resp = client.post("/auth/signup", json=data)
    assert resp.status_code == 422
    error_msg = {
        "errors": [
            {
                "field": "password",
                "message": "Provided password too short must be >= 8",
                "error_type": "string",
            }
        ]
    }
    assert resp.json() == error_msg


def test_invalid_password_no_lowercase(client, data):
    data["password"] = "AWE123!!"
    resp = client.post("/auth/signup", json=data)
    assert resp.status_code == 422
    error_msg = {
        "errors": [
            {
                "field": "password",
                "message": "password must contain lowercase letters",
                "error_type": "string",
            }
        ]
    }
    assert resp.json() == error_msg


def test_invalid_password_no_uppercase(client, data):
    data["password"] = "deadpool@123!"
    resp = client.post("/auth/signup", json=data)
    assert resp.status_code == 422
    error_msg = {
        "errors": [
            {
                "field": "password",
                "message": "password must contain uppercase letters",
                "error_type": "string",
            }
        ]
    }
    assert resp.json() == error_msg


def test_invalid_password_no_valid_char(client, data):
    data["password"] = "qwertAqwe123%_%"
    resp = client.post("/auth/signup", json=data)
    assert resp.status_code == 422


def test_invalid_firstname(client, data):
    data["first_name"] = "1string"
    resp = client.post("/auth/signup", json=data)
    assert resp.status_code == 422


def test_invalid_lastname(client, data):
    data["last_name"] = "1string"
    resp = client.post("/auth/signup", json=data)
    assert resp.status_code == 422

def test_create_user_already_exists(client, data):
    with TestingSessionLocal() as session:
        try:
            response = client.post(
                "/auth/signup",
                json=data
            )
            assert response.status_code == 400
            assert response.json() == {"message": "User with email already exists"}
        except IntegrityError:
            session.rollback()
            raise

