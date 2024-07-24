from fastapi import APIRouter, Request


router = APIRouter(prefix="/movies")



@router.get("", response_class=)