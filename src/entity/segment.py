from dataclasses import dataclass

import pygame

from src.geometry.line import Line
from src.geometry.point import Point
from src.type import Color

from .entity import Entity
from .ids import EntityId
from .station import Station


@dataclass
class StationPair:
    start: Station
    end: Station


@dataclass
class PointPair:
    start: Point
    end: Point


class Segment(Entity):
    __slots__ = (
        "color",
        "stations",
        "points",
        "line",
    )
    stations: StationPair | None
    points: PointPair
    line: Line

    def __init__(self, color: Color, id: EntityId) -> None:
        super().__init__(id)
        self.color = color
        self.stations = None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Segment) and self.id == other.id

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.line.draw(surface)
