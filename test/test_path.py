import unittest
from math import ceil
from typing import Final
from unittest.mock import create_autospec

import pygame

from src.config import metro_speed_per_ms
from src.entity import Metro, Path, Station, get_random_station, get_random_stations
from src.geometry.point import Point
from src.passengers_mediator import PassengersMediator
from src.utils import get_random_color, get_random_position, get_random_station_shape

from test.base_test import BaseTestCase
from test.legacy_access import legacy_path_draw_with_order, legacy_path_segments

# some tests break under lower/higher framerate
# TODO: analize why
framerate: Final = 60
dt_ms: Final = ceil(1000 / framerate)


class TestPath(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.width, self.height = 640, 480
        self.screen = create_autospec(pygame.surface.Surface)
        self.position = get_random_position(self.width, self.height)
        self.color = get_random_color()
        self.passengers_mediator = PassengersMediator()

    def tearDown(self) -> None:
        super().tearDown()

    def test_init(self) -> None:
        path = Path(get_random_color(), 0)
        station = get_random_station(self.passengers_mediator)
        path.add_station(station)

        self.assertIn(station, path.stations)

    def test_draw(self) -> None:
        path = Path(get_random_color(), 0)
        stations = get_random_stations(5, self.passengers_mediator)
        for station in stations:
            path.add_station(station)
        legacy_path_draw_with_order(path, self.screen, 0)

        self.assertEqual(self._draw.line.call_count, 4 + 3)

    def test_draw_temporary_point(self) -> None:
        path = Path(get_random_color(), 0)
        path.add_station(get_random_station(self.passengers_mediator))
        path.set_temporary_point(Point(1, 1))
        legacy_path_draw_with_order(path, self.screen, 0)

        self.assertEqual(self._draw.line.call_count, 1)

    def test_metro_starts_at_beginning_of_first_line(self) -> None:
        path = Path(get_random_color(), 0)
        path.add_station(get_random_station(self.passengers_mediator))
        path.add_station(get_random_station(self.passengers_mediator))
        legacy_path_draw_with_order(path, self.screen, 0)
        metro = Metro(self.passengers_mediator)
        path.add_metro(metro)

        self.assertEqual(metro.current_segment, legacy_path_segments(path)[0])
        assert metro.travel_step
        self.assertEqual(
            metro.travel_step.current,
            legacy_path_segments(path)[0],
        )
        self.assertTrue(metro.is_forward)

    def test_metro_moves_from_beginning_to_end(self) -> None:
        path = Path(get_random_color(), 0)
        path.add_station(
            Station(get_random_station_shape(), Point(0, 0), self.passengers_mediator)
        )
        dist_in_one_sec = 1000 * metro_speed_per_ms
        path.add_station(
            Station(
                get_random_station_shape(),
                Point(dist_in_one_sec, 0),
                self.passengers_mediator,
            )
        )
        legacy_path_draw_with_order(path, self.screen, 0)

        for station in path.stations:
            station.draw(self.screen)
        metro = Metro(self.passengers_mediator)
        path.add_metro(metro)

        for _ in range(framerate):
            path.move_metro(metro, dt_ms)

        self.assertTrue(path.stations[1].contains(metro.position))

    def test_metro_turns_around_when_it_reaches_the_end(self) -> None:
        path = Path(get_random_color(), 0)
        path.add_station(
            Station(get_random_station_shape(), Point(0, 0), self.passengers_mediator)
        )
        dist_in_one_sec = 1000 * metro_speed_per_ms
        path.add_station(
            Station(
                get_random_station_shape(),
                Point(dist_in_one_sec, 0),
                self.passengers_mediator,
            )
        )
        legacy_path_draw_with_order(path, self.screen, 0)
        for station in path.stations:
            station.draw(self.screen)
        metro = Metro(self.passengers_mediator)
        path.add_metro(metro)

        for _ in range(framerate + 1):
            path.move_metro(metro, dt_ms)

        self.assertFalse(metro.is_forward)

    def test_metro_loops_around_the_path(self) -> None:
        path = Path(get_random_color(), 0)
        path.add_station(
            Station(get_random_station_shape(), Point(0, 0), self.passengers_mediator)
        )
        dist_in_one_sec = 1000 * metro_speed_per_ms
        path.add_station(
            Station(
                get_random_station_shape(),
                Point(dist_in_one_sec, 0),
                self.passengers_mediator,
            )
        )
        path.add_station(
            Station(
                get_random_station_shape(),
                Point(dist_in_one_sec, dist_in_one_sec),
                self.passengers_mediator,
            )
        )
        path.add_station(
            Station(
                get_random_station_shape(),
                Point(0, dist_in_one_sec),
                self.passengers_mediator,
            )
        )
        path.set_loop()
        legacy_path_draw_with_order(path, self.screen, 0)
        for station in path.stations:
            station.draw(self.screen)
        metro = Metro(self.passengers_mediator)
        path.add_metro(metro)

        for station_idx in [1, 2, 3, 0, 1]:
            for _ in range(framerate):
                path.move_metro(metro, dt_ms)

            self.assertTrue(path.stations[station_idx].contains(metro.position))


if __name__ == "__main__":
    unittest.main()
