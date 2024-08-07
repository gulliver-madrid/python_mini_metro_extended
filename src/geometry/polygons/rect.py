from shortuuid import uuid

from src.geometry.point import Point
from src.geometry.type import ShapeType
from src.type import Color

from .polygon import Polygon


class Rect(Polygon):
    __slots__ = ("width", "height")

    def __init__(self, color: Color, width: int, height: int) -> None:
        left = round(-width * 0.5)
        right = round(width * 0.5)
        top = round(-height * 0.5)
        bottom = round(height * 0.5)
        points = [
            Point(left, top),
            Point(right, top),
            Point(right, bottom),
            Point(left, bottom),
        ]
        super().__init__(ShapeType.RECT, color, points)
        self.id = f"Rect-{uuid()}"
        self.color = color
        self.width = width
        self.height = height
