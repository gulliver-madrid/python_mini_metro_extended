import math

from src.geometry.point import Point
from src.geometry.polygon import Polygon
from src.geometry.type import ShapeType
from src.type import Color

COS_30_DEGREES = math.cos(math.radians(30))


class Triangle(Polygon):
    # Equilateral triangle
    def __init__(self, color: Color, size: int) -> None:
        half_size = round(size / 2)
        points = [
            Point(-half_size, round(-COS_30_DEGREES * half_size)),
            Point(half_size, round(-COS_30_DEGREES * half_size)),
            Point(0, round(COS_30_DEGREES * half_size)),
        ]
        super().__init__(ShapeType.TRIANGLE, color, points)
