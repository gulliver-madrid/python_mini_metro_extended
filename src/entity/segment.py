from __future__ import annotations

from abc import ABC

import pygame
from shortuuid import uuid  # type: ignore

from src.config import screen_height, screen_width
from src.entity.station import Station
from src.geometry.line import Line
from src.geometry.point import Point
from src.type import Color


class Segment(ABC):
    def __init__(self, color: Color) -> None:
        self.id = f"Segment-{uuid()}"
        self.color = color
        self.start_station: Station | None = None
        self.end_station: Station | None = None
        self.segment_start: Point
        self.segment_end: Point
        self.line: Line

    def __eq__(self, other: Segment) -> bool:
        return self.id == other.id

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.line.draw(surface)
