from typing import List
from uuid import uuid4

import pygame
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry.polygon import Polygon as ShapelyPolygon

from geometry.point import Point
from geometry.shape import Shape
from geometry.type import ShapeType
from type import Color


class Polygon(Shape):
    def __init__(self, color: Color, points: List[Point]) -> None:
        super().__init__(ShapeType.POLYGON)
        self.id = f"Polygon-{uuid4()}"
        self.color = color
        self.points = points

    def draw(self, surface: pygame.surface.Surface, position: Point) -> None:
        super().draw(surface, position)
        points = self.points
        tuples = []
        for i in range(len(points)):
            points[i] += position
            tuples.append(points[i].to_tuple())
        pygame.draw.polygon(surface, self.color, tuples)

    def contains(self, point: Point) -> bool:
        point = ShapelyPoint(point.left, point.top)
        tuples = [x.to_tuple() for x in self.points]
        polygon = ShapelyPolygon(tuples)
        return polygon.contains(point)
