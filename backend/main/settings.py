import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

if os.getenv("TEST_DB") == "1":
    USERNAME = os.getenv("TEST_USERNAME")
    DATABASE = os.getenv("TEST_DATABASE")
    HOST = os.getenv("TEST_HOST")
    PASSWORD = os.getenv("TEST_PASSWORD")
    PORT =  3306

else:
    USERNAME = os.getenv("USERNAME")
    DATABASE = os.getenv("DATABASE")
    HOST = os.getenv("DATABASE_HOST")
    PASSWORD = os.getenv("DATABASE_PASSWORD")

    PORT = int(os.getenv("PORT", 3306))


DATABASE_DICT = {
    "USERNAME": USERNAME,
    "PASSWORD": PASSWORD,
    "DATABASE": DATABASE,
    "HOST": HOST,
    "PORT": PORT
}

# redis hosting platform
REDIS_HOST=os.getenv("REDIS_HOST", "localhost")
REDIS_PASSWORD=os.getenv("REDIS_PASSWORD", "")
REDIS_PORT=int(os.getenv("REDIS_PORT", 6379))

HOST_APP= "http://localhost:8000"


# cryptography hash
KEY = os.getenv("CY_KEY", 'JokaPNHDNcQbH3MOYGPyVbHoANFkcYjglRm7rYqjILY=')


#JWT secret key
ACCESS_TOKEN_SECRET_KEY = os.getenv("ACCESS_TOKEN_SECRET_KEY") or "JokaPNHDNcQbH3MOYGPyVbHoANFkcYjglRm7rYqjILY="
REFRESH_TOKEN_SECRET_KEY = os.getenv("REFRESH_TOKEN_SECRET_KEY") or "JokaPNHDNcQbH3MOYGPyVbHoANFkcYjglRm7rYqjILY="
# access token and refresh token in minute
ACCESS_TOKEN_IN_MIN = int(os.getenv("ACCESS_TOKEN_IN_MIN", 1))
REFRESH_TOKEN_IN_MIN = int(os.getenv("REFRESH_TOKEN_IN_MIN", 1440))
