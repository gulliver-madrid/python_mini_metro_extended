import unittest
from copy import deepcopy
from unittest.mock import create_autospec

import pygame

from src.config import Config
from src.geometry.circle import Circle
from src.geometry.line import Line
from src.geometry.point import Point
from src.geometry.rect import Rect
from src.geometry.triangle import Triangle
from src.geometry.types import Degrees
from src.utils import get_random_color, get_random_position

from test.base_test import BaseTestCase


class TestGeometry(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.width, self.height = Config.screen_width, Config.screen_height
        self.screen = create_autospec(pygame.surface.Surface)
        self.position = get_random_position(self.width, self.height)
        self.color = get_random_color()
        self.points = [Point(-1, -1), Point(0, 2), Point(2, -1)]
        self.start = get_random_position(self.width, self.height)
        self.end = get_random_position(self.width, self.height)
        self.linewidth = 1

    def tearDown(self) -> None:
        super().tearDown()

    def test_circle_init(self) -> None:
        radius = 1
        circle = Circle(self.color, radius)

        self.assertSequenceEqual(circle.color, self.color)
        self.assertEqual(circle.radius, radius)

    def init_circle(self) -> Circle:
        return Circle(self.color, 1)

    def test_circle_draw(self) -> None:
        circle = self.init_circle()
        circle.draw(self.screen, self.position)

        self._draw.circle.assert_called_once()

    def test_circle_contains_point(self) -> None:
        circle = self.init_circle()
        circle.draw(self.screen, self.position)

        self.assertTrue(
            circle.contains(self.position + Point(circle.radius - 1, circle.radius - 1))
        )
        self.assertFalse(
            circle.contains(self.position + Point(circle.radius + 1, circle.radius + 1))
        )

    def test_rect_init(self) -> None:
        width = 2
        height = 3
        rect = Rect(self.color, width, height)

        self.assertSequenceEqual(rect.color, self.color)
        self.assertEqual(rect.width, width)
        self.assertEqual(rect.height, height)

    def init_rect(self) -> Rect:
        return Rect(self.color, 10, 20)

    def test_rect_draw(self) -> None:
        rect = self.init_rect()
        rect.draw(self.screen, self.position)

        self._draw.polygon.assert_called_once()

    def test_rect_contains_point(self) -> None:
        rect = self.init_rect()
        rect.draw(self.screen, self.position)

        self.assertTrue(rect.contains(rect.position + Point(1, 1)))
        self.assertFalse(rect.contains(rect.position + Point(rect.width, rect.height)))

    def test_rect_rotate(self) -> None:
        rect = self.init_rect()
        rect.draw(self.screen, self.position)
        rect_points = deepcopy(rect.points)
        rect.rotate(Degrees(180))
        # this do nothing to points because the rotation logic
        # is actually inside `Rect.draw` method
        for point in rect.points:
            self.assertIn(point, rect_points)
        rect.rotate(Degrees(180))
        self.assertSequenceEqual(rect.points, rect_points)

    def test_rect_set_degrees(self) -> None:
        rect = self.init_rect()
        rect.draw(self.screen, self.position)
        rect_points = deepcopy(rect.points)
        rect.set_degrees(Degrees(180))
        # this do nothing to points because the rotation logic
        # is actually inside `Rect.draw` method
        for point in rect.points:
            self.assertIn(point, rect_points)
        rect.set_degrees(Degrees(360))
        self.assertSequenceEqual(rect.points, rect_points)

    def test_line_init(self) -> None:
        line = Line(self.color, self.start, self.end, self.linewidth)

        self.assertSequenceEqual(line.color, self.color)
        self.assertEqual(line.start, self.start)
        self.assertEqual(line.end, self.end)
        self.assertEqual(line.width, self.linewidth)

    def init_line(self) -> Line:
        return Line(self.color, self.start, self.end, self.linewidth)

    def test_line_draw(self) -> None:
        line = self.init_line()
        line.draw(self.screen)

        self._draw.line.assert_called_once()

    def test_triangle_init(self) -> None:
        size = 10
        triangle = Triangle(self.color, size)

        self.assertSequenceEqual(triangle.color, self.color)

    def init_triangle(self) -> Triangle:
        return Triangle(self.color, 10)

    def test_triangle_draw(self) -> None:
        triangle = self.init_triangle()
        triangle.draw(self.screen, self.position)

        self._draw.polygon.assert_called_once()


if __name__ == "__main__":
    unittest.main()
