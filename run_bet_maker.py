import asyncio
import uvicorn

from bet_maker.mq import MessageQueue
from bet_maker.redis_controller import RedisController
from bet_maker.app import app
from common import config as app_config


async def run():
    r = RedisController()
    mq = MessageQueue(r)
    consumer = asyncio.create_task(mq.start_consumer())

    config = uvicorn.Config(
        app, host="0.0.0.0", port=app_config.BET_MAKER_PORT, log_level="info"
    )
    server = uvicorn.Server(config)
    try:
        await server.serve()
    finally:
        consumer.cancel()
        try:
            await consumer
        except asyncio.CancelledError:
            print("Consumer task successfully cancelled")


if __name__ == "__main__":
    asyncio.run(run())
