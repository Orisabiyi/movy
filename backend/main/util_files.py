import secrets
from typing import List

from cryptography.fernet import Fernet
from fastapi import Request
from main import settings
from movies.models import Movie
from movies.schemas import MovieListSchemas
from passlib.hash import argon2

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


def movie_schema_list(request: Request, movies: List[Movie]):
    m_list = [
        MovieListSchemas(
            **{
                "id": movie.id,
                "title": movie.title,
                "tagline": movie.tag_line,
                "runtime": f"{movie.duration_in_min // 60}hr {movie.duration_in_min % 60}min",
                "release_date": str(movie.release_date),
                "poster_path": movie.poster_path,
                "url": f"{request.base_url}{movie.get_path}",
            }
        )
        for movie in movies
    ]
    return m_list
