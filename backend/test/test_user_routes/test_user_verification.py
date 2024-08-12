"""
- TEST USER account action is working
- TEST activation link is working only once
- TEST user token is not invalid
- TEST invalid email is not passed
"""
from main.email_context import context
from test.conftest import TestingSessionLocal
from main.utils import hash_password, _encode_token, _decode_token
from users.models import User
import pytest


def test_user_account_activation(client, data, user):
    """test user account get activated"""
    token = user.get_context_string(context.USER_VERIFICATION_ACCOUNT)
    hashed_token = hash_password(token).encode()

    data = {
        "id": _encode_token(user.email.encode()),
        "token":  _encode_token(hashed_token)
    }

    resp = client.post('/auth/verify-account', json=data)
    assert resp.status_code == 200
    with TestingSessionLocal() as session:
        user_activate = session.query(User).filter(User.email == user.email).first()
        assert user_activate.is_verified is True #type: ignore
 

def test_token_does_not_activate_user_twice(client, data,  user):
    """test user token is not used twice"""
    token = user.get_context_string(context.USER_VERIFICATION_ACCOUNT)
    hashed_token = hash_password(token).encode()

    data = {
        "id": _encode_token(user.email.encode()),
        "token":  _encode_token(hashed_token)
    }

    resp = client.post('/auth/verify-account', json=data)
    assert resp.status_code == 400


def test_token_is_invalid(client, data, user):
    """ test if invalid token is provided"""
    token = user.get_context_string(context.USER_VERIFICATION_ACCOUNT)
    hashed_token = hash_password(token).encode()

    data = {
        "id": _encode_token(user.email.encode()),
        "token":  _encode_token(hashed_token + "nqkwk".encode())
    }

    resp = client.post('/auth/verify-account', json=data)
    assert resp.status_code == 400


def test_invalid_id_provided(client, data, user):
    """ test invalid id passed"""
    token = user.get_context_string(context.USER_VERIFICATION_ACCOUNT)
    hashed_token = hash_password(token).encode()

    data = {
        "id": _encode_token("kelanidara@gmail.com".encode()),
        "token":  _encode_token(hashed_token + "nqkwk".encode())
    }

    resp = client.post('/auth/verify-account', json=data)
    assert resp.status_code == 400