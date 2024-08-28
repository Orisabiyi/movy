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
    PORT = 3306

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
    "PORT": PORT,
}

DEBUG = os.getenv("DEBUG")
TEST_DB=os.getenv("TEST_DB")

MY_SSL_CERT = os.getenv("MY_SSL_CERT") or ""
# redis hosting platform
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_USER = os.getenv("REDIS_USER", "")
REDIS_URI = os.getenv("REDIS_URI", "")
HOST_APP = "http://localhost:8000" if DEBUG else "https://movy-sigma.vercel.app"


# cryptography hash
KEY = os.getenv("CY_KEY", "JokaPNHDNcQbH3MOYGPyVbHoANFkcYjglRm7rYqjILY=")


# JWT secret key
ACCESS_TOKEN_SECRET_KEY = (
    os.getenv("ACCESS_TOKEN_SECRET_KEY")
    or "JokaPNHDNcQbH3MOYGPyVbHoANFkcYjglRm7rYqjILY="
)
REFRESH_TOKEN_SECRET_KEY = (
    os.getenv("REFRESH_TOKEN_SECRET_KEY")
    or "JokaPNHDNcQbH3MOYGPyVbHoANFkcYjglRm7rYqjILY="
)
# access token and refresh token in minute
ACCESS_TOKEN_IN_MIN = int(os.getenv("ACCESS_TOKEN_IN_MIN", 1))
REFRESH_TOKEN_IN_MIN = int(os.getenv("REFRESH_TOKEN_IN_MIN", 1440))

DEBUG = os.getenv("DEBUG") == "1"

HASH_ID_SALT = os.getenv("HASHID_SALT") or "vnn1kn123fnnvknvei1;[]123!fekf"


# class auth cred
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or ""
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET") or ""
SESSION_SECRET = os.getenv("SESSION_SECRET") or ""
OAUTH_PASSWORD=os.getenv("OAUTH_PASSWORD")

PAYSTACK_SECRET_KEY=os.getenv("PAYSTACK_SECRET_KEY") or ""