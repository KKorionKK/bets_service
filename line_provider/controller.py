import decimal
from fastapi.exceptions import HTTPException
from fastapi import status
from typing import Optional

from common.schemas import Event, EventUpdate, UpdatedEventDTO
from common.enumerations import EventState
from common import tools


class EventsController:
    """
    Синглтон для работы с событиями.
    """

    __test_events = [
        Event(coefficient=1.2, deadline=tools.get_now_timestamp() + 600),
        Event(coefficient=1.15, deadline=tools.get_now_timestamp() + 60),
        Event(coefficient=1.67, deadline=tools.get_now_timestamp() + 90),
    ]
    __events: dict[str, Event] = {}

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(EventsController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self.__events:
            self.__events = {item.id: item for item in self.__test_events}

    @classmethod
    def get_initial_events(cls) -> list[Event]:
        return cls.__test_events

    def check_is_event_exists_and_return_if_exists(
        self, event_id: str
    ) -> Optional[Event]:
        if event_id not in self.__events.keys():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )
        else:
            return self.__events[event_id]

    def get_events(self) -> list[Event]:
        return list(self.__events.values())

    def add_event(self, event: Event) -> None:
        if event.id in self.__events.keys():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event with this id already exists",
            )
        if event.deadline <= tools.get_now_timestamp():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deadline must be in the future",
            )
        if event.coefficient <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coefficient must be more than 1",
            )
        self.__events[event.id] = event

    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        event = self.__events[event_id]
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
            )
        return event

    def remove_event_by_id(self, event_id: str) -> Optional[Event]:
        self.check_is_event_exists_and_return_if_exists(event_id)
        del self.__events[event_id]

    def change_coefficient_by_id(
        self, event_id: str, new_coefficient: decimal.Decimal
    ) -> Optional[Event]:
        if new_coefficient <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coefficient must be more than 1",
            )
        self.__events[event_id].coefficient = new_coefficient
        return self.__events[event_id]

    def change_status_by_id(
        self, event_id: str, new_status: EventState
    ) -> Optional[Event]:
        self.__events[event_id].state = new_status
        return self.__events[event_id]

    def update_event(self, updated_event: EventUpdate) -> Optional[UpdatedEventDTO]:
        event = self.check_is_event_exists_and_return_if_exists(updated_event.id)
        model = UpdatedEventDTO()
        if (
            updated_event.new_state != event.state
            and updated_event.new_state is not None
        ):
            self.change_status_by_id(updated_event.id, updated_event.new_state)
            model.stated_changed = True
        if (
            updated_event.new_coefficient != event.coefficient
            and updated_event.new_coefficient is not None
        ):
            self.change_coefficient_by_id(
                updated_event.id, updated_event.new_coefficient
            )
            model.coefficient_changed = True
        upd = self.get_event_by_id(updated_event.id)
        model.event = upd
        return model
