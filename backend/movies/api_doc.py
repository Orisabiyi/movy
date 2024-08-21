lst_movie_response = {
    200: {
        "description": "Successful response with movie listings",
        "content": {
            "application/json": {
                "example": {
                    "total": 160,
                    "next": "http://127.0.0.1:8000/?page=2",
                    "prev": None,
                    "total_pages": 8,
                    "pages_remaining": 7,
                    "page_size": 20,
                    "results": [
                        {
                            "id": 2,
                            "title": "Deadpool & Wolverine",
                            "tagline": "Come together.",
                            "runtime": "2hr 8min",
                            "release_date": "2024-07-24",
                            "poster_path": "https://image.tmdb.org/t/p/original/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg",
                            "url": "/movies/2",
                        },
                        # Other movie entries
                    ],
                }
            }
        },
    },
    400: {
        "description": "Unsuccessful response for movie listing",
        "content": {
            "application/json": {
                "example": {
                    "total": 0,
                    "next": None,
                    "prev": None,
                    "total_pages": 0,
                    "pages_remaining": 0,
                    "page_size": 0,
                    "results": [],
                }
            }
        },
    },
}


movie_detail_response = {
    200: {
        "description": "movie found successful response",
        "content": {
            "application/json": {
                "example": {
                    "id": "eX9Gw8MaWJjWqD7YkOvJ",
                    "title": "Deadpool & Wolverine",
                    "description": "A listless Wade Wilson toils away in civilian life with his days as the morally flexible mercenary, Deadpool, behind him. But when his homeworld faces an existential threat, Wade must reluctantly suit-up again with an even more reluctant Wolverine.",
                    "tag_line": "Come together.",
                    "runtime": "2hr 8min",
                    "release_date": "2024-07-24",
                    "trailer_link": "https://www.youtube.com/watch?v=Yd47Z8HYf0Y",
                    "poster_path": "https://image.tmdb.org/t/p/original/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg",
                    "backdrop_path": "https://image.tmdb.org/t/p/original/9l1eZiJHmhr5jIlthMdJN5WYoff.jpg",
                    "genres": ["Action", "Science Fiction", "Comedy"],
                    "starring": [
                        {
                            "name": "Ryan Reynolds",
                            "profile_path": "https://image.tmdb.org/t/p/original/2Orm6l3z3zukF1q0AgIOUqvwLeB.jpg",
                        },
                        {
                            "name": "Hugh Jackman",
                            "profile_path": "https://image.tmdb.org/t/p/original/oX6CpXmnXCHLyqsa4NEed1DZAKx.jpg",
                        },
                        {
                            "name": "Emma Corrin",
                            "profile_path": "https://image.tmdb.org/t/p/original/w4gFlPOqdSMRSH1dsuqQMKCGBWg.jpg",
                        },
                    ],
                    "more_actors": "and more...",
                }
            }
        },
    },
    404: {
        "description": "Movie not found",
        "content": {
            "application/json": {
                "example": {"message": "Movie with this id not found"}
            }
        },
    },
}


movie_search = {
    200: {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "example": [
                    {
                        "id": "eX9Gw8MaWJjWqD7YkOvJ" ,
                        "title": "Deadpool",
                        "tagline": "Feel the love.",
                        "runtime": "1hr 48min",
                        "release_date": "2016-02-09",
                        "poster_path": "https://image.tmdb.org/t/p/original/3E53WEZJqP6aM84D8CckXx4pIHw.jpg",
                        "url": "http://127.0.0.1:8000/movies/10",
                    },
                    {
                        "id": "eX9Gw8MaWJjWqD7YkOvJ",
                        "title": "Once Upon a Deadpool",
                        "tagline": "Yule believe in miracles.",
                        "runtime": "1hr 58min",
                        "release_date": "2018-12-11",
                        "poster_path": "https://image.tmdb.org/t/p/original/5Ka49BWWyKMXr93YMbH5wLN7aAM.jpg",
                        "url": "http://127.0.0.1:8000/movies/27",
                    },
                ]
            }
        },
    },
    404: {
        "description": "Unsuccessful Response",
        "content": {
            "application/json": {
                "example": {"message": "Movie with moom not found"}
            }
        },
    },
}
