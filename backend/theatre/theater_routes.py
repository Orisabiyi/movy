from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.responses import JSONResponse
from main.auth import Auth
from main.database import DB, get_db
from fastapi.responses import JSONResponse
from main.auth import Auth
from main.database import DB, get_db

from .models import Theatre, TheatreReviewRating, Address


router = APIRouter(prefix="/theatre", tags=["theatre"])