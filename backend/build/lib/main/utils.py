import secrets

from passlib.hash import argon2
from cryptography.fernet import Fernet
from main import settings

cypher_token = Fernet(settings.KEY)

def unique_string(byte: int = 10) -> str:
    return secrets.token_urlsafe(byte)


def hash_password(password: str):
    return argon2.hash(password)


def _verify_hash_password(password: str, hashed_password: str):
    return argon2.verify(password, hashed_password)


def _decode_token(encrpt: bytes) -> str:
    return cypher_token.decrypt(encrpt).decode()

def _encode_token(encrypt_text: bytes) -> str:
    return cypher_token.encrypt(encrypt_text).decode()