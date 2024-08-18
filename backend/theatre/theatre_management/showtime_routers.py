from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/theatre", tags=["THEATRE MANAGEMENT"])


@router.post("/create-show")
def theatre_create_show():
    ...


# @router.post("/")