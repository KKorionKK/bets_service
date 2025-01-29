import enum


class EventState(enum.Enum):
    NEW = 1
    WON = 2
    LOSE = 3


class MessageType(enum.Enum):
    NEW_EVENT = 1
    EVENT_STATE_CHANGED = 2
    EVENT_COEFFICIENT_CHANGED = 3
    INITIAL = 4
