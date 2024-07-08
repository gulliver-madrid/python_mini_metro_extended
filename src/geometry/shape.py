from __future__ import annotations

from abc import ABC, abstractmethod

import pygame
from shortuuid import uuid

from src.geometry.point import Point
from src.geometry.type import ShapeType
from src.type import Color


class Shape(ABC):
    def __init__(self, type: ShapeType, color: Color):
        self.type = type
        self.color = color
        self.id = f"Shape-{uuid()}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Shape) and self.id == other.id

    @abstractmethod
    def draw(self, surface: pygame.surface.Surface, position: Point) -> None:
        self.position = position

    @abstractmethod
    def contains(self, point: Point) -> bool:
        pass

    def rotate(self, degree_diff: float) -> None:
        pass

    def set_degrees(self, degrees: float) -> None:
        pass
