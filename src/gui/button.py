from abc import ABC, abstractmethod

import pygame

from src.geometry.point import Point
from src.geometry.shape import Shape


class Button(ABC):
    def __init__(self, shape: Shape) -> None:
        super().__init__()
        self.shape = shape
        self.position: Point

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.shape.draw(surface, self.position)

    def contains(self, point: Point) -> bool:
        return self.shape.contains(point)

    @abstractmethod
    def on_hover(self) -> None:
        pass

    @abstractmethod
    def on_exit(self) -> None:
        pass

    @abstractmethod
    def on_click(self) -> None:
        pass
