# isort: skip_file

from __future__ import annotations

from typing import Any, List, Sequence

import pygame
from shapely.geometry import Point as ShapelyPoint  # type: ignore [import-untyped]
from shapely.geometry.polygon import (  # type: ignore [import-untyped]
    Polygon as ShapelyPolygon,
)
from shortuuid import uuid
from typing_extensions import override

from src.config import Config
from src.geometry.point import Point
from src.geometry.shape import Shape
from src.geometry.type import ShapeType
from src.geometry.types import Degrees, create_degrees
from src.type import Color


class Polygon(Shape):
    __slots__ = ("points", "degrees")

    def __init__(
        self, shape_type: ShapeType, color: Color, points: Sequence[Point]
    ) -> None:
        super().__init__(shape_type, color)
        self.id = f"Polygon-{uuid()}"
        self.points = points
        self.degrees: Degrees = create_degrees(0)

    @override
    def draw(self, surface: pygame.surface.Surface, position: Point) -> None:
        super()._set_position(position)
        tuples: List[tuple[float, float]] = []
        for point in self.points:
            rotated_point = point.rotate(self.degrees)
            tuples.append((rotated_point + self.position).to_tuple())
        pygame.draw.polygon(
            surface, self.color, tuples, width=1 if Config.unfilled_shapes else 0
        )

    def contains(self, point: Point) -> bool:
        shapely_point: Any = ShapelyPoint(point.left, point.top)
        tuples = [(x + self.position).to_tuple() for x in self.points]
        polygon: Any = ShapelyPolygon(tuples)
        result = polygon.contains(shapely_point)
        assert isinstance(result, bool)
        return result

    def set_degrees(self, degrees: Degrees) -> None:
        self.degrees = degrees

    def rotate(self, degree_diff: Degrees) -> None:
        self.degrees = create_degrees(self.degrees + degree_diff)

    def get_scaled(self, f: float) -> Polygon:
        return Polygon(
            self.type, self.color, [Point(p.left * f, p.top * f) for p in self.points]
        )
