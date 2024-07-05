import math
from typing import List

import pygame
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry.polygon import Polygon as ShapelyPolygon
from shortuuid import uuid

from src.config import Config
from src.geometry.point import Point
from src.geometry.shape import Shape
from src.geometry.type import ShapeType
from src.type import Color


class Polygon(Shape):
    def __init__(
        self, shape_type: ShapeType, color: Color, points: List[Point]
    ) -> None:
        super().__init__(shape_type, color)
        self.id = f"Polygon-{uuid()}"
        self.points = points
        self.degrees: float = 0

    def draw(self, surface: pygame.surface.Surface, position: Point) -> None:
        super().draw(surface, position)
        tuples = []
        for point in self.points:
            rotated_point = point.rotate(self.degrees)
            tuples.append((rotated_point + self.position).to_tuple())
        pygame.draw.polygon(
            surface, self.color, tuples, width=1 if Config.unfilled_shapes else 0
        )

    def contains(self, point: Point) -> bool:
        shapely_point = ShapelyPoint(point.left, point.top)
        tuples = [(x + self.position).to_tuple() for x in self.points]
        polygon = ShapelyPolygon(tuples)
        result = polygon.contains(shapely_point)
        assert isinstance(result, bool)
        return result

    def set_degrees(self, degrees: float) -> None:
        self.degrees = degrees

    def rotate(self, degree_diff: float) -> None:
        self.degrees += degree_diff
