#!/usr/bin/env python3
"""
handle fetching of data from TMDB database using its API
"""
import json
import os
from typing import Dict, List, Optional, Union

import requests
from dotenv import load_dotenv
from main.database import DB
from main.settings import ENV_PATH
from movies.models import (
    Cast,
    Country,
    # Gender,
    Genre,
    Language,
    Movie,
    ProductionCompany,
)
from sqlalchemy import Tuple

db = DB()

load_dotenv(dotenv_path=ENV_PATH)


ACCESS_TOKEN = os.getenv("TMDB_ACCESS_READ_TOKEN")


def _get_url_response(url: str, headers: Dict, params: Dict) -> Dict:
    resp = requests.get(url, headers=headers, params=params)
    assert resp.status_code == 200, f"{resp.text}, {resp.status_code}"
    return resp.json()


class TMDB:
    def __init__(self):
        self._url = "https://api.themoviedb.org/3/"
        self._headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        }
        self.param = {"api_key": os.getenv("TMDB_API_KEY")}
        self._movie_id_lst = []

    def get_movie_genre(self):
        url = f"{self._url}genre/movie/list?language=en"
        response = _get_url_response(url, self._headers, self.param)
        genres = response["genres"]
        for genre in genres:
            genre = Genre(name=genre["name"])
            db._session.add(genre)
        db._session.commit()
        db._close

    def get_country(self):
        url = f"{self._url}configuration/countries?language=en-US"
        response = _get_url_response(url, self._headers, self.param)
        countries = response
        for country in countries:
            country = Country(name=country["english_name"])
            db._session.add(country)
        db._session.commit()
        db._close

    def get_popular_movies(self):
        """
        get all movies in tmdb
        """
        movie_info = {}
        movie_id_lst = []
        for i in range(1, 5):
            url = f"{self._url}movie/popular?language=en-US&page={i}"
            resp = _get_url_response(url, self._headers, self.param)
            movies = resp["results"]
            for movie in movies:
                trailer_link = self.get_trailer_link(movie["id"])

                movie_detail = self.get_movie_detail(movie["id"])
                poster_path = f"https://image.tmdb.org/t/p/original{movie['poster_path']}"
                backdrop_path = f"https://image.tmdb.org/t/p/original{movie['backdrop_path']}"
                movie_info = {
                    "title": movie["title"],
                    "description": movie["overview"],
                    "poster_path": poster_path,
                    "backdrop_path": backdrop_path,
                    "trailer_link": trailer_link,
                    "release_date": movie["release_date"],
                    "duration_in_min": movie_detail["runtime"],
                    "tag_line": movie_detail["tagline"]
                }
                movie_obj = db.add(Movie, close=False, **movie_info)
                movie_id_lst.append((movie["id"], movie_obj.id))
                self.prod_company(
                    movie_detail["production_companies"], movie_obj
                )
                self.add_genre(movie_detail["genres"], movie_obj)
        self.movie_id_lst = movie_id_lst

    def get_trailer_link(self, movie_id: int) -> Optional[str]:
        """
        get video trailer link by movie_id
        """
        url = f"{self._url}movie/{movie_id}/videos?language=en-US"
        resp = _get_url_response(url, self._headers, self.param)

        trailer = resp["results"]

        key = None
        for value in trailer:
            trailer_type = value["type"]
            name = value["name"]
            if value["type"] == trailer_type or value["name"] == name:
                key = value["key"]
        if not key:
            return None
        return f"https://www.youtube.com/watch?v={key}"

    def get_movie_detail(self, movie_id: int):
        """
        get movie details from the database
        """
        url = f"{self._url}movie/{movie_id}?language=en-US"
        resp = _get_url_response(url, self._headers, self.param)
        return resp

    def get_language(self):
        url = f"{self._url}configuration/languages"
        resp = _get_url_response(url, headers=self._headers, params=self.param)

        for lang in resp:
            db.add(Language, lang=lang["english_name"])

    def prod_company(
        self, prod_company: List[Dict[str, Union[str, int]]], movie_obj: Movie
    ):
        for company in prod_company:
            pc = db.get_or_add(
                ProductionCompany,
                close=False,
                name=company["name"],
            )
            movie_obj.movie_production_com.append(pc)
        db._session.commit()

    def add_genre(
        self, movie_genre: List[Dict[str, Union[str, int]]], movie_obj: Movie
    ):
        for genre in movie_genre:
            gen = db.get_or_add(Genre, close=False, name=genre["name"])
            movie_obj.movie_genres.append(gen)
        db._session.commit()
        db._close

    def movie_cast(self):
        movie_id_lst = self.movie_id_lst
        cast = None
        for movie_id in movie_id_lst:
            url = f"{self._url}movie/{movie_id[0]}/credits?language=en-US"
            resp = _get_url_response(url, self._headers, self.param)
            cast_info = resp["cast"]
            for cast_d in cast_info:
                cast_dep = cast_d["known_for_department"]
                if cast_dep == "Acting":
                    cast = db.get_or_add(
                        Cast,
                        close=False,
                        original_name=cast_d["original_name"],
                        popularity_name=cast_d["name"],
                    )
                movie_obj = db.get(Movie, id=movie_id[1])
                if cast:
                    cast.casts_movie.append(movie_obj)
        db._session.commit()
        db._close

if __name__ == "__main__":
    tmdb = TMDB()
    # tmdb.get_movie()
    tmdb.get_movie_genre()
    tmdb.get_language()
    tmdb.get_country()
    tmdb.get_popular_movies()
    tmdb.movie_cast()
