import random
import unittest
from unittest.mock import Mock

import numpy as np
import pygame

from test.random_seed_config import RANDOM_SEED


class FixedRandomSeedTestCase(unittest.TestCase):
    def setUp(self) -> None:
        random.seed(RANDOM_SEED)
        np.random.seed(RANDOM_SEED)


class BaseTestCase(FixedRandomSeedTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.__original_draw = pygame.draw
        self._draw = Mock()
        pygame.draw = self._draw

    def tearDown(self) -> None:
        pygame.draw = self.__original_draw
