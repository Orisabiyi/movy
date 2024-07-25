from fastapi import FastAPI
from .database import DB
from movies.views import router

app = FastAPI()

db = DB()