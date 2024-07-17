import math

from src.geometry.point import Point
from src.geometry.polygon import Polygon
from src.geometry.type import ShapeType
from src.type import Color

COS_30_DEGREES = math.cos(math.radians(30))


class Triangle(Polygon):
    def __init__(self, color: Color, size: int) -> None:
        # Equilateral triangle
        self.size = size
        points = [
            Point(-size, round(-COS_30_DEGREES * size)),
            Point(size, round(-COS_30_DEGREES * size)),
            Point(0, round(COS_30_DEGREES * size)),
        ]
        super().__init__(ShapeType.TRIANGLE, color, points)
