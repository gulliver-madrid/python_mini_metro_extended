import os
import sys
import unittest
from unittest.mock import MagicMock, create_autospec

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")

import pygame

from geometry.circle import Circle
from geometry.line import Line
from geometry.polygon import Polygon
from geometry.rect import Rect
from utils import get_random_color, get_random_position


class TestGeometry(unittest.TestCase):
    def setUp(self):
        self.width, self.height = 640, 480
        self.screen = create_autospec(pygame.Surface)
        self.position = get_random_position(self.width, self.height)
        self.color = get_random_color()
        self.points = [
            get_random_position(self.width, self.height),
            get_random_position(self.width, self.height),
            get_random_position(self.width, self.height),
        ]
        self.start = get_random_position(self.width, self.height)
        self.end = get_random_position(self.width, self.height)
        self.linewidth = 1

    def test_circle_init(self):
        radius = 1
        circle = Circle(self.color, radius)
        self.assertSequenceEqual(circle.color, self.color)
        self.assertEqual(circle.radius, radius)

    def init_circle(self):
        return Circle(self.color, 1)

    def test_circle_draw(self):
        circle = self.init_circle()
        pygame.draw.circle = MagicMock()
        circle.draw(self.screen, self.position)
        pygame.draw.circle.assert_called_once()

    def test_rect_init(self):
        width = 2
        height = 3
        rect = Rect(self.color, width, height)
        self.assertSequenceEqual(rect.color, self.color)
        self.assertEqual(rect.width, width)
        self.assertEqual(rect.height, height)

    def init_rect(self):
        return Rect(self.color, 2, 3)

    def test_rect_draw(self):
        rect = self.init_rect()
        pygame.draw.rect = MagicMock()
        rect.draw(self.screen, self.position)
        pygame.draw.rect.assert_called_once()

    def test_polygon_init(self):
        polygon = Polygon(self.color, self.points)
        self.assertSequenceEqual(polygon.color, self.color)
        self.assertSequenceEqual(polygon.points, self.points)

    def init_polygon(self):
        return Polygon(self.color, self.points)

    def test_polygon_draw(self):
        polygon = self.init_polygon()
        pygame.draw.polygon = MagicMock()
        polygon.draw(self.screen, self.position)
        pygame.draw.polygon.assert_called_once()

    def test_line_init(self):
        line = Line(self.color, self.start, self.end, self.linewidth)
        self.assertSequenceEqual(line.color, self.color)
        self.assertDictEqual(line.start, self.start)
        self.assertDictEqual(line.end, self.end)
        self.assertEqual(line.width, self.linewidth)

    def init_line(self):
        return Line(self.color, self.start, self.end, self.linewidth)

    def test_line_draw(self):
        line = self.init_line()
        pygame.draw.line = MagicMock()
        line.draw(self.screen)
        pygame.draw.line.assert_called_once()


if __name__ == "__main__":
    unittest.main()