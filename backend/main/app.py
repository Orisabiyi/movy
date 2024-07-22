from fastapi import FastAPI
from .database import DB


app = FastAPI()

db = DB()