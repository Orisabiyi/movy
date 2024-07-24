#!/usr/bin/env python3
"""
handle fetching of data from TMDB Access token
"""
import json
import os
from typing import Dict, Optional

import requests
from dotenv import load_dotenv
from main.database import DB
from main.settings import ENV_PATH
from movies.models import Cast, Country, Genre, Movie

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
        image_base_url = "https://image.tmdb.org/t/p/"
        movie_id_lst = []
        page_number = 1
        movie_info = {}
        movie_id_lst = []
        for i in range(1, 5):
            url = f"{self._url}movie/popular?language=en-US&page={page_number}"
            resp = _get_url_response(url, self._headers, self.param)
            movies = resp["results"]

            for movie in movies:
                movie_id_lst.append(movie["id"])
                trailer_link = self.get_trailer_link(movie["id"])

                movie_detail = self.get_movie_detail(movie['id'])
                poster_path = f"https://image.tmdb.org/t/p/original{movie['poster_path']}"
                backdrop_path = f"https://image.tmdb.org/t/p/original{movie['backdrop_path']}"
                movie_info = {
                    "title": movie["title"],
                    "description": movie["overview"],
                    "poster_path": poster_path,
                    "backdrop_path": backdrop_path,
                    "trailer_link": trailer_link,
                    "release_date": movie["release_date"],
                    "duration_in_min": movie_detail["runtime"]
                }
        print(movie_info)
    def get_trailer_link(self, movie_id: int) -> Optional[str]:
        """
        get video trailer link by movie_id
        """
        url = f"{self._url}movie/{movie_id}/videos?language=en-US"
        resp = _get_url_response(url, self._headers, self.param)

        trailer = resp['results']

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

if __name__ == "__main__":
    tmdb = TMDB()
    # tmdb.get_movie()
    tmdb.get_movie_genre()
    tmdb.get_country()
    tmdb.get_popular_movies()
