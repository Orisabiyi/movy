import os
from test.conftest import EMAIL, FIRST_NAME, LAST_NAME, PASSWORD

import pytest


@pytest.fixture
def data():
    return {
        "first_name": FIRST_NAME,
        "last_name": LAST_NAME,
        "email": EMAIL,
        "password": PASSWORD,
    }


def test_create_user(client, data):
    data["email"] = "kelanidarasimi@gmail.com"
    print(data, "----------->")
    resp = client.post("/auth/signup", json=data)
    assert resp.status_code == 201
    assert "password" not in resp.json()


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
    data["password"] = "AWE123!"
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


def test_invalid_firstname(client): ...


def test_invalid_lastname(client): ...
