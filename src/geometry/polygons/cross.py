from src.geometry.point import Point
from src.geometry.type import ShapeType
from src.type import Color

from .polygon import Polygon


class Cross(Polygon):
    __slots__ = ()

    def __init__(self, color: Color, size: int, width: int = 0) -> None:
        half_size = round(size / 2)
        if width == 0:
            width = round(2 * half_size / 3)

        W = width
        L = round(0.5 * (2 * half_size - W))
        points = [
            Point(L, 0),
            Point(L + W, 0),
            Point(L + W, L),
            Point(2 * L + W, L),
            Point(2 * L + W, L + W),
            Point(L + W, L + W),
            Point(L + W, 2 * L + W),
            Point(L, 2 * L + W),
            Point(L, L + W),
            Point(0, L + W),
            Point(0, L),
            Point(L, L),
        ]
        for i in range(len(points)):
            points[i] += Point(-half_size, -half_size)
        super().__init__(ShapeType.CROSS, color, points)
