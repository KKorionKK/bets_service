from fastapi import APIRouter, Depends
from fastapi.background import BackgroundTasks
from typing import Optional
from line_provider.controller import EventsController
from line_provider.mq import MessageQueue
from common.schemas import Event, EventUpdate

events_route = APIRouter(prefix="/event", tags=["Event route"])

mq = MessageQueue()


@events_route.get("/")
async def get_events(
    controller: EventsController = Depends(EventsController),
) -> list[Event]:
    """
    Получение событий
    :return: list[Event]
    """
    events = controller.get_events()
    return events


@events_route.get("/{event_id}")
async def get_event_by_id(
    event_id: str,
    controller: EventsController = Depends(EventsController),
) -> Optional[Event]:
    """
    Получение события по ID
    :return: Event
    """
    return controller.get_event_by_id(event_id)


@events_route.post("/")
async def create_event(
    event: Event,
    background_tasks: BackgroundTasks,
    controller: EventsController = Depends(EventsController),
) -> list[Event]:
    """
    Создание события, в фоне после запроса происходит отправка в BetMaker. Есть проверки на требования к данным
    :return: Обновленный список событий
    """
    controller.add_event(event)
    background_tasks.add_task(mq.send_new_event, event=event)
    return controller.get_events()


@events_route.patch("/")
async def update_event(
    event: EventUpdate,
    background_tasks: BackgroundTasks,
    controller: EventsController = Depends(EventsController),
) -> Event:
    """
    Обновление события. Тут так же как и в POST /event есть проверка данных.
    :return: Обновленное событие
    """
    updates = controller.update_event(event)
    if updates.stated_changed:
        background_tasks.add_task(
            mq.send_new_state, event_id=updates.event.id, state=updates.event.state
        )
    if updates.coefficient_changed:
        background_tasks.add_task(
            mq.send_new_coefficient,
            event_id=updates.event.id,
            new_coefficient=updates.event.coefficient,
        )
    return updates.event
