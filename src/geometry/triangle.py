from src.geometry.point import Point
from src.geometry.polygon import Polygon
from src.geometry.type import ShapeType
from src.type import Color


class Triangle(Polygon):
    def __init__(self, color: Color, size: int) -> None:
        # Equilateral triangle
        self.size = size
        points = [
            Point(-size, round(-0.866 * size)),
            Point(size, round(-0.866 * size)),
            Point(0, round(0.866 * size)),
        ]
        super().__init__(ShapeType.TRIANGLE, color, points)
