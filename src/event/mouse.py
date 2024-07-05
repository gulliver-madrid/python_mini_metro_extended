from src.event.event import Event
from src.event.type import MouseEventType
from src.geometry.point import Point


class MouseEvent(Event):
    def __init__(self, event_type: MouseEventType, position: Point) -> None:
        super().__init__(event_type)
        self.position = position
