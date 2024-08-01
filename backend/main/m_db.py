import os

import redis
from dotenv import load_dotenv
from main.settings import ENV_PATH, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

load_dotenv(dotenv_path=ENV_PATH)

REDIS_CLI = redis.StrictRedis(
    # host=REDIS_HOST,
    # port=REDIS_PORT,
    # password='',
    # decode_responses=True  # Decode responses to strings (default is bytes)
)

# Test the connection when the module is imported
# try:
#     response = REDIS_CLI.ping()
#     if response:
#         print("Connected to Redis successfully!")
# except redis.AuthenticationError:
#     raise redis.AuthenticationError("Authentication Error: Could not authenticate with Redis.")
# except redis.ConnectionError:
#     raise redis.ConnectionError("Connection Error: Could not connect to Redis.")
# except Exception as e:
#     raise Exception(f"An error occurred: {e}")