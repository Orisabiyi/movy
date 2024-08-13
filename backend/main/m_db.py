import os

import redis
from dotenv import load_dotenv
from main.settings import (
    DEBUG,
    ENV_PATH,
    REDIS_HOST,
    REDIS_PASSWORD,
    REDIS_PORT,
    REDIS_URI,
    REDIS_USER,
)

if not DEBUG:
    # REDIS_CLI = redis.Redis(
    #     host=REDIS_HOST,
    #     port=REDIS_PORT,
    #     password=REDIS_PASSWORD,
    # )
    REDIS_CLI = redis.from_url(REDIS_URI)
    try:
        response = REDIS_CLI.ping()
        if response:
            print("Connected to Redis successfully!")
    except redis.AuthenticationError:
        raise redis.AuthenticationError(
            "Authentication Error: Could not authenticate with Redis."
        )
    except redis.ConnectionError:
        raise redis.ConnectionError(
            "Connection Error: Could not connect to Redis."
        )
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

else:
    REDIS_CLI = redis.Redis()
