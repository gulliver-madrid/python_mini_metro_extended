import pygame

from src.geometry.line import Line
from src.geometry.point import Point
from src.type import Color

from .entity import Entity
from .ids import EntityId
from .station import Station


class Segment(Entity):
    __slots__ = (
        "color",
        "start_station",
        "end_station",
        "segment_start",
        "segment_end",
        "line",
    )
    start_station: Station | None
    end_station: Station | None
    segment_start: Point
    segment_end: Point
    line: Line

    def __init__(self, color: Color, id: EntityId) -> None:
        super().__init__(id)
        self.color = color
        self.start_station = None
        self.end_station = None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Segment) and self.id == other.id

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.line.draw(surface)
