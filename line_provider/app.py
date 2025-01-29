import uvicorn
from fastapi import FastAPI

from line_provider.routes import events_route
from line_provider.controller import EventsController
from line_provider.lifespan import lifespan

events = EventsController()

app = FastAPI(lifespan=lifespan)

app.include_router(events_route)

if __name__ == "__main__":
    uvicorn.run(app)
