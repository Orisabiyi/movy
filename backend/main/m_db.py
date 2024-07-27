import os

import redis
from dotenv import load_dotenv
from main.settings import ENV_PATH

load_dotenv(dotenv_path=ENV_PATH)


REDIS_CLI = redis.Redis()