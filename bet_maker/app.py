from fastapi import FastAPI

from bet_maker.routes import events_router, bets_router

app = FastAPI()
app.include_router(events_router)
app.include_router(bets_router)
