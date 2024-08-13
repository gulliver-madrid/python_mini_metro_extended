import unittest

from src.geometry.circle import Circle
from src.geometry.line import Line
from src.geometry.point import Point
from src.geometry.polygons import Rect, Triangle


class TestGeometryBasics(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.color = (0, 0, 0)
        self.start = Point(200, 300)
        self.end = Point(500, 400)
        self.linewidth = 1

    def tearDown(self) -> None:
        super().tearDown()

    ######################
    ### tests ############
    ######################

    def test_circle_init(self) -> None:
        radius = 1
        circle = Circle(self.color, radius)

        self.assertSequenceEqual(circle.color, self.color)
        self.assertEqual(circle.radius, radius)

    def test_rect_init(self) -> None:
        width = 2
        height = 3
        rect = Rect(self.color, width, height)

        self.assertSequenceEqual(rect.color, self.color)
        self.assertEqual(rect.width, width)
        self.assertEqual(rect.height, height)

    def test_line_init(self) -> None:
        line = Line(self.color, self.start, self.end, self.linewidth)

        self.assertSequenceEqual(line.color, self.color)
        self.assertEqual(line.start, self.start)
        self.assertEqual(line.end, self.end)
        self.assertEqual(line.width, self.linewidth)

    def test_triangle_init(self) -> None:
        size = 10
        triangle = Triangle(self.color, size)

        self.assertSequenceEqual(triangle.color, self.color)


if __name__ == "__main__":
    unittest.main()
