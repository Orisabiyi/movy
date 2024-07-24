#!/usr/bin/env python3
"""
handle fetching of data from the api by fetching
"""
import requests
import json

url = "https://advance-movie-api.p.rapidapi.com/api/v1/streamitfree/genres/1"

headers = {
	"x-rapidapi-key": "c8d745a222msh02932c4e8d26ecdp197b56jsnb19b2a158823",
	"x-rapidapi-host": "advance-movie-api.p.rapidapi.com",
	"X-RapidAPI-Proxy-Secret": "4d633e10-2ff4-11ef-a338-672c018612df"
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    raise Exception(f"Unsuccessful response {response.status_code}")


genres = response.json()["result"]["data"]


movie_file = "movie_data.json" # for testing purposes the productiion will be fetching from a live data api
for genre in genres:
    url = f"https://advance-movie-api.p.rapidapi.com/api/v1/streamitfree/genres/{genre}/17"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Unsuccessful response {response.status_code}")

    # data = response.json()[]
    # with open(movie_file, "w") as mv:
    #     json.dump(mv,)