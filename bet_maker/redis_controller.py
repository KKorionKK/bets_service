import redis.asyncio as redis
from typing import Optional
from common import config, tools
from common.schemas import (
    Event,
    BetCreateSchema,
    NewStateDTO,
    NewCoefficientDTO,
    BetSchema,
)

from fastapi.exceptions import HTTPException
from fastapi import status


class RedisController:
    """
    Класс для взаимодействия с редисом.
    """

    EVENTS_KEY = "event"
    BETS_KEY = "bet"
    UPDATED_AT_KEY = "dt".encode()

    def __init__(self):
        self.redis = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            password=config.REDIS_PASSWORD,
            username=config.REDIS_USERNAME,
            decode_responses=True,
        )

    async def __save_dt(self):
        dt = tools.get_now_timestamp()
        await self.redis.set(self.UPDATED_AT_KEY, dt)

    async def flush(self):
        await self.redis.flushdb()

    async def save_new_event(self, event: Event) -> None:
        await self.redis.hset(
            f"{self.EVENTS_KEY}-{event.id}",
            mapping=event.model_dump_unconvertable_fields(),
        )

    async def bulk_save_events(self, events: list[Event]) -> None:
        pipeline = await self.redis.pipeline()
        for event in events:
            pipeline.hset(
                f"{self.EVENTS_KEY}-{event.id}",
                mapping=event.model_dump_unconvertable_fields(),
            )
        await pipeline.execute()

    async def change_event_status(self, dto: NewStateDTO) -> None:
        name = f"{self.EVENTS_KEY}-{dto.event_id}"
        await self.redis.hset(name, "state", dto.new_state.value)
        await self._update_event_bets_states(dto)

    async def change_event_coefficient(self, dto: NewCoefficientDTO) -> None:
        name = f"{self.EVENTS_KEY}-{dto.event_id}"
        await self.redis.hset(name, "coefficient", str(dto.new_coefficient))

    async def _update_event_bets_states(self, dto: NewStateDTO):
        names = await self.redis.keys(f"{self.BETS_KEY}-{dto.event_id}-*")
        pipeline = await self.redis.pipeline()
        for name in names:
            pipeline.hset(name, "state", dto.new_state.value)
        await pipeline.execute()

    async def make_bet(self, bet: BetCreateSchema) -> Optional[str]:
        raw_event: dict = await self.redis.hgetall(f"{self.EVENTS_KEY}-{bet.event_id}")

        if raw_event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )
        event = Event.from_redis(raw_event)

        if event.deadline < tools.get_now_timestamp():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can not bet on event after a deadline.",
            )

        dto = BetSchema(
            event_id=bet.event_id, amount=bet.amount, coefficient=event.coefficient
        )

        await self.redis.hset(
            f"{self.BETS_KEY}-{event.id}-{dto.bet_id}",
            mapping=dto.model_dump_unconvertable_fields(),
        )
        return dto.bet_id

    async def get_bets(self) -> list[BetSchema]:
        keys = await self.redis.keys(f"*{self.BETS_KEY}*")  # O(N)
        pipeline = await self.redis.pipeline(transaction=False)
        for key in keys:
            pipeline.hgetall(key)
        res = await pipeline.execute()
        bets = [BetSchema.from_redis(bet) for bet in res]
        return bets

    async def get_events(self) -> list[Event]:
        now = tools.get_now_timestamp()

        keys = await self.redis.keys(f"*{self.EVENTS_KEY}*")  # O(N)
        pipeline = await self.redis.pipeline(transaction=False)
        for key in keys:
            pipeline.hgetall(key)
        res = await pipeline.execute()

        events = [Event.from_redis(event) for event in res]
        return list(filter(lambda event: event.deadline > now, events))
