from uuid import uuid4

import pygame

from geometry.point import Point
from geometry.shape import Shape


class Passenger:
    def __init__(self, destination_shape: Shape) -> None:
        self.id = f"Passenger-{uuid4()}"
        self.position = Point(0, 0)
        self.destination_shape = destination_shape

    def __repr__(self) -> str:
        return self.id

    def draw(self, surface: pygame.surface.Surface):
        self.destination_shape.draw(surface, self.position)
