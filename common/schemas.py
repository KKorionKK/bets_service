import decimal
from pydantic import BaseModel, Field
from typing import Optional

from common import tools
from common.enumerations import EventState, MessageType


class Event(BaseModel):
    id: str = Field(default_factory=tools.get_uuid)
    coefficient: Optional[decimal.Decimal] = None
    deadline: Optional[int] = None
    state: Optional[EventState] = EventState.NEW

    created_at: int = Field(default_factory=tools.get_now_timestamp)

    def model_dump_unconvertable_fields(self, *args, **kwargs):
        data = self.model_dump(*args, **kwargs)
        data["coefficient"] = str(self.coefficient)
        data["state"] = self.state.value
        return data

    @classmethod
    def from_redis(cls, data: dict[str, str]):
        data["state"] = EventState(int(data["state"]))
        return cls(**data)


class EventUpdate(BaseModel):
    id: str
    new_coefficient: Optional[decimal.Decimal] = None
    new_state: Optional[EventState] = None


class BetCreateSchema(BaseModel):
    event_id: str
    amount: decimal.Decimal


class NewStateDTO(BaseModel):
    event_id: str
    new_state: EventState


class NewCoefficientDTO(BaseModel):
    event_id: str
    new_coefficient: decimal.Decimal


class MessageDTO(BaseModel):
    type: MessageType
    payload: Event | NewStateDTO | NewCoefficientDTO | list[Event]

    id: str = Field(default_factory=tools.get_uuid)


class UpdatedEventDTO(BaseModel):
    event: Event = None
    stated_changed: bool = False
    coefficient_changed: bool = False


class BetSchema(BaseModel):
    event_id: str
    amount: decimal.Decimal
    coefficient: decimal.Decimal
    state: EventState = EventState.NEW

    bet_id: str = Field(default_factory=tools.get_uuid)
    created_at: int = Field(default_factory=tools.get_now_timestamp)

    @classmethod
    def from_redis(cls, data: dict):
        data["state"] = EventState(int(data["state"]))
        return cls(**data)

    def model_dump_unconvertable_fields(self, *args, **kwargs):
        data = self.model_dump(*args, **kwargs)
        data["coefficient"] = str(self.coefficient)
        data["state"] = self.state.value
        data["amount"] = str(self.amount)
        return data
