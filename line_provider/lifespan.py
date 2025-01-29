from contextlib import asynccontextmanager
from fastapi import FastAPI
from line_provider.mq import MessageQueue
from line_provider.controller import EventsController


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    При каждом перезапуске BetMaker в целях синхронизации чистим Redis.
    """
    mq = MessageQueue()
    await mq.send_initial_events(EventsController.get_initial_events())
    print("Sent initial events")
    yield
