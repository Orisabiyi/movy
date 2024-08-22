from hashids import Hashids
from typing import Union, Tuple
from fastapi import HTTPException
from .settings import HASH_ID_SALT

hash = Hashids(salt=HASH_ID_SALT, min_length=20)


def encode_id(id:  int) -> str:
   return hash.encode(id)


def decode_id(id: str) -> int:

    ha = hash.decode(id)
    if not ha:
        raise HTTPException(status_code=401, detail={"message": "invalid id provided found"})
    return ha[0]