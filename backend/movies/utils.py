from typing import List
from fastapi import Request
from .models import Movie
from .schemas import MovieListSchemas
from main.hash_id import encode_id

"""
this function was added here because I do not understand why vscode is throwin import error
while import the functon from main.utils
"""
def movie_schema_list(request: Request, movies: List[Movie]):
    m_list = [
        MovieListSchemas(
            **{
                "id": encode_id(movie.id),
                "title": movie.title,
                "tagline": movie.tag_line,
                "runtime": f"{movie.duration_in_min // 60}hr {movie.duration_in_min % 60}min",
                "description": movie.description,
                "release_date": str(movie.release_date),
                "poster_path": movie.poster_path,
                "url": f"{request.base_url}{movie.get_path}",
            }
        )
        for movie in movies
    ]
    return m_list
