import pygame
from shortuuid import uuid

from src.geometry.point import Point
from src.type import Color


class Line:
    __slots__ = (
        "id",
        "color",
        "start",
        "end",
        "width",
    )

    def __init__(self, color: Color, start: Point, end: Point, width: int) -> None:
        self.id = f"Line-{uuid()}"
        self.color = color
        self.start = start
        self.end = end
        self.width = width

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Line) and self.id == other.id

    def draw(self, surface: pygame.surface.Surface) -> pygame.Rect:
        return pygame.draw.line(
            surface, self.color, self.start.to_tuple(), self.end.to_tuple(), self.width
        )
