from __future__ import annotations

import pygame

from src.geometry.line import Line
from src.geometry.point import Point
from src.type import Color

from .entity import Entity
from .ids import EntityId
from .station import Station


class Segment(Entity):

    def __init__(self, color: Color, id: EntityId) -> None:
        super().__init__(id)
        self.color = color
        self.start_station: Station | None = None
        self.end_station: Station | None = None
        self.segment_start: Point
        self.segment_end: Point
        self.line: Line

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Segment) and self.id == other.id

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.line.draw(surface)
