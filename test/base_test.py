import random
import unittest
from collections.abc import Sequence
from unittest.mock import Mock

import numpy as np
import pygame

from src.engine.engine import Engine
from src.entity.station import Station
from src.event.mouse import MouseEvent
from src.event.type import MouseEventType
from src.geometry.point import Point
from src.reactor import UI_Reactor

from test.legacy_access import legacy_get_engine_stations
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


class GameplayBaseTestCase(BaseTestCase):
    reactor: UI_Reactor
    engine: Engine

    def _replace_stations(self, stations: Sequence[Station]) -> None:
        legacy_get_engine_stations(self.engine).clear()
        legacy_get_engine_stations(self.engine).extend(stations)

    def _send_event_to_station(
        self,
        event_type: MouseEventType,
        station_idx: int,
        modified: Point | None = None,
    ) -> None:
        position = legacy_get_engine_stations(self.engine)[station_idx].position
        if modified:
            position += modified
        self.reactor.react(MouseEvent(event_type, position))

    def _connect_stations(self, station_indexes: Sequence[int]) -> None:
        self._send_event_to_station(MouseEventType.MOUSE_DOWN, station_indexes[0])
        for idx in station_indexes[1:]:
            self._send_event_to_station(MouseEventType.MOUSE_MOTION, idx)
        self._send_event_to_station(MouseEventType.MOUSE_UP, station_indexes[-1])
