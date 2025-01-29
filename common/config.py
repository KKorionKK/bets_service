import os
from pathlib import Path
from dotenv import dotenv_values

environment = os.getenv("ENV")
env = dotenv_values(str(Path().absolute()) + "/.env")

# RabbitMQ
AMQP_USERNAME = env.get("AMQP_USERNAME")
AMQP_PASSWORD = env.get("AMQP_PASSWORD")
AMQP_HOST = env.get("AMQP_HOST")
AMQP_PORT = env.get("AMQP_PORT")
AMQP_VIRTUALHOST = env.get("AMQP_VIRTUALHOST")
AMQP_QUEUE = env.get("AMQP_QUEUE")

# Redis
REDIS_USERNAME = env.get("REDIS_USERNAME")
REDIS_PASSWORD = env.get("REDIS_PASSWORD")
REDIS_HOST = env.get("REDIS_HOST")
REDIS_PORT = env.get("REDIS_PORT")

# Services
LINE_PROVIDER_PORT = int(env.get("LINE_PROVIDER_PORT"))
BET_MAKER_PORT = int(env.get("BET_MAKER_PORT"))
