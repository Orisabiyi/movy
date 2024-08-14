
# def get_movie_detail_in_dict(movie_dict):
#     del dct["_sa_instance_state"]
#     del dct["uploaded_at"]
#     dct = {
#         "id": dct["id"],
#         "title": dct["title"],
#         "description": dct["description"],
#         "poster_path": dct["poster_path"],
#         "backdrop_path": dct["backdrop_path"],
#         "tag_line": dct["tag_line"],
#         "trailer_link": dct["trailer_link"],
#         "runtime": f"{dct['duration_in_min']// 60}hr {dct['duration_in_min'] % 60}min",
#         "release_date": str(dct["release_date"]),
#         "genres": [genre.name for genre in dct["movie_genres"]],
#         # "starring": [
#         #     {"name": dct["movie_casts"][i].name, "profile_path": dct["movie_casts"][i].profile_path}
#         #     for i in range(1, 11)
#         # ],
#     }
#     return dct