from src.event.event import Event
from src.event.type import KeyboardEventType


class KeyboardEvent(Event):
    def __init__(self, event_type: KeyboardEventType, key: int) -> None:
        super().__init__(event_type)
        self.key = key
