import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

USERNAME = os.getenv("TEST_USERNAME")
DATABASE = os.getenv("TEST_DATABASE")
HOST = os.getenv("TEST_HOST")
PASSWORD = os.getenv("TEST_PASSWORD")

if os.getenv("TEST_DB") != "1":
    USERNAME = os.getenv("USERNAME")
    DATABASE = os.getenv("DATABASE")
    HOST = os.getenv("HOST")
    PASSWORD = os.getenv("PASSWORD")

PORT: int = int(os.getenv("PORT", 3306))


DATABASE_DICT = {
    "USERNAME": USERNAME,
    "PASSWORD": PASSWORD,
    "DATABASE": DATABASE,
    "HOST": HOST,
    "PORT": PORT
}