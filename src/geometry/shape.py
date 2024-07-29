from abc import ABC, abstractmethod
from typing import final

import pygame
from shortuuid import uuid

from src.geometry.point import Point
from src.geometry.type import ShapeType
from src.type import Color


class Shape(ABC):
    __slots__ = (
        "type",
        "color",
        "id",
        "position",
    )

    def __init__(self, type: ShapeType, color: Color):
        self.type = type
        self.color = color
        self.id = f"Shape-{uuid()}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Shape) and self.id == other.id

    @abstractmethod
    def draw(self, surface: pygame.surface.Surface, position: Point) -> None:
        raise NotImplementedError

    @abstractmethod
    def contains(self, point: Point) -> bool:
        raise NotImplementedError

    @final
    def _set_position(self, position: Point) -> None:
        self.position = position
