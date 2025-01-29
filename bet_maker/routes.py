from fastapi import APIRouter, Depends
from bet_maker.redis_controller import RedisController

from common.schemas import Event, BetCreateSchema, BetSchema


events_router = APIRouter(prefix="/events", tags=["Events router"])
bets_router = APIRouter(prefix="/bet", tags=["Bets router"])

"""
PS Не добавлена авторизация, так как не требует ТЗ, да и делаем максимально простой сервис.
"""


@events_router.get("/")
async def get_events(
    controller: RedisController = Depends(RedisController),
) -> list[Event]:
    """
    Получение списка событий
    :return: list[Event]
    """
    events = await controller.get_events()
    return events


@bets_router.get("/")
async def get_bets(
    controller: RedisController = Depends(RedisController),
) -> list[BetSchema]:
    """
    Получение истории всех ставок
    :return: list[BetSchema]
    """
    bets = await controller.get_bets()
    return bets


@bets_router.post("/")
async def create_bet(
    schema: BetCreateSchema, controller: RedisController = Depends(RedisController)
) -> str:
    """
    Создание ставки на событие
    :return: ID ставки
    """
    return await controller.make_bet(schema)
