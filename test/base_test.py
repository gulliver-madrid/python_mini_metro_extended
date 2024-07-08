import unittest
from unittest.mock import Mock

import pygame


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.__original_draw = pygame.draw
        self._draw = Mock()
        pygame.draw = self._draw

    def tearDown(self) -> None:
        pygame.draw = self.__original_draw
