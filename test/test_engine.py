import unittest
from math import ceil
from typing import Any, Final
from unittest.mock import Mock, create_autospec, patch

import pygame

from src.config import Config, station_color, station_size
from src.engine.engine import Engine
from src.engine.passenger_spawner import PassengerSpawner
from src.entity import Station, get_random_stations
from src.event.mouse import MouseEvent
from src.event.type import MouseEventType
from src.geometry.circle import Circle
from src.geometry.point import Point
from src.geometry.polygons import Rect, Triangle
from src.geometry.type import ShapeType
from src.reactor import UI_Reactor
from src.utils import get_random_color, get_random_position

from test.base_test import GameplayBaseTestCase

# some tests break under lower/higher framerate
# TODO: analize why
framerate: Final = 60
dt_ms: Final = ceil(1000 / framerate)


class TestEngine(GameplayBaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.width, self.height = Config.screen_width, Config.screen_height
        self.screen = create_autospec(pygame.surface.Surface)
        self.position = get_random_position(self.width, self.height)
        self.color = get_random_color()
        self.engine = Engine()
        self.reactor = UI_Reactor(self.engine)
        self.engine.render(self.screen)

    def tearDown(self) -> None:
        super().tearDown()

    def test_react_mouse_down(self) -> None:
        for station in self.engine.stations:
            station.draw(self.screen)
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_DOWN, Point(-1, -1)))

        self.assertTrue(self.reactor.is_mouse_down)

    def test_get_containing_entity(self) -> None:
        self.assertTrue(
            self.engine.get_containing_entity(
                self.engine.stations[2].position + Point(1, 1)
            )
        )

    def test_react_mouse_up(self) -> None:
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_UP, Point(-1, -1)))

        self.assertFalse(self.reactor.is_mouse_down)

    def test_passengers_are_added_to_stations(self) -> None:
        self.engine._passenger_spawner._spawn_passengers()  # pyright: ignore [reportPrivateUsage]

        self.assertEqual(len(self.engine.passengers), len(self.engine.stations))

    @patch.object(PassengerSpawner, "_spawn_passengers", new_callable=Mock)
    def test_is_passenger_spawn_time(self, mock_spawn_passengers: Any) -> None:
        # Run the game until first wave of passengers spawn
        times_needed = Config.passenger_spawning.interval_step * framerate
        for _ in range(
            ceil(times_needed / Config.passenger_spawning.first_time_divisor)
        ):
            self.engine.increment_time(dt_ms)

        mock_spawn_passengers.assert_called_once()

        for _ in range(times_needed):
            self.engine.increment_time(dt_ms)

        self.assertEqual(
            mock_spawn_passengers.call_count,
            2,
        )

    def test_passengers_spawned_at_a_station_have_a_different_destination(self) -> None:
        # Run the game until first wave of passengers spawn
        times_needed = Config.passenger_spawning.interval_step * framerate
        for _ in range(
            ceil(times_needed / Config.passenger_spawning.first_time_divisor)
        ):
            self.engine.increment_time(dt_ms)

        assert self.engine.passengers

        for station in self.engine.stations:
            for passenger in station.passengers:
                self.assertNotEqual(
                    passenger.destination_shape.type, station.shape.type
                )

    def test_passengers_at_connected_stations_have_a_way_to_destination(self) -> None:
        self.engine.stations.clear()
        self.engine.stations.extend(
            [
                Station(
                    Rect(
                        color=station_color,
                        width=station_size,
                        height=station_size,
                    ),
                    Point(100, 100),
                    self.engine.passengers_mediator,
                ),
                Station(
                    Circle(
                        color=station_color,
                        radius=round(station_size / 2),
                    ),
                    Point(100, 200),
                    self.engine.passengers_mediator,
                ),
            ]
        )
        # Need to draw stations if you want to override them
        for station in self.engine.stations:
            station.draw(self.screen)

        # Run the game until first wave of passengers spawn
        for _ in range(Config.passenger_spawning.interval_step):
            self.engine.increment_time(dt_ms)

        self._connect_stations([0, 1])
        self.engine.increment_time(dt_ms)

        for passenger in self.engine.passengers:
            self.assertIn(passenger, self.engine.travel_plans)
            self.assertIsNotNone(passenger.travel_plan)
            assert passenger.travel_plan
            self.assertIsNotNone(passenger.travel_plan.next_path)
            self.assertIsNotNone(passenger.travel_plan.next_station)

    def test_passengers_at_isolated_stations_have_no_way_to_destination(self) -> None:
        # Run the game until first wave of passengers spawn, then 1 more frame
        for _ in range(Config.passenger_spawning.interval_step + 1):
            self.engine.increment_time(dt_ms)

        for passenger in self.engine.passengers:
            self.assertIn(passenger, self.engine.travel_plans)
            self.assertIsNotNone(passenger.travel_plan)
            assert passenger.travel_plan
            self.assertIsNone(passenger.travel_plan.next_path)
            self.assertIsNone(passenger.travel_plan.next_station)

    def test_get_station_for_shape_type(self) -> None:
        self.engine.stations.clear()
        self.engine.stations.extend(
            [
                Station(
                    Rect(
                        color=station_color,
                        width=station_size,
                        height=station_size,
                    ),
                    get_random_position(self.width, self.height),
                    self.engine.passengers_mediator,
                ),
                Station(
                    Circle(
                        color=station_color,
                        radius=round(station_size / 2),
                    ),
                    get_random_position(self.width, self.height),
                    self.engine.passengers_mediator,
                ),
                Station(
                    Circle(
                        color=station_color,
                        radius=round(station_size / 2),
                    ),
                    get_random_position(self.width, self.height),
                    self.engine.passengers_mediator,
                ),
                Station(
                    Triangle(
                        color=station_color,
                        size=station_size,
                    ),
                    get_random_position(self.width, self.height),
                    self.engine.passengers_mediator,
                ),
                Station(
                    Triangle(
                        color=station_color,
                        size=station_size,
                    ),
                    get_random_position(self.width, self.height),
                    self.engine.passengers_mediator,
                ),
                Station(
                    Triangle(
                        color=station_color,
                        size=station_size,
                    ),
                    get_random_position(self.width, self.height),
                    self.engine.passengers_mediator,
                ),
            ]
        )
        rect_stations = self.engine.path_manager._travel_plan_finder._get_stations_for_shape_type(  # pyright: ignore [reportPrivateUsage]
            ShapeType.RECT
        )
        circle_stations = self.engine.path_manager._travel_plan_finder._get_stations_for_shape_type(  # pyright: ignore [reportPrivateUsage]
            ShapeType.CIRCLE
        )
        triangle_stations = self.engine.path_manager._travel_plan_finder._get_stations_for_shape_type(  # pyright: ignore [reportPrivateUsage]
            ShapeType.TRIANGLE
        )

        self.assertCountEqual(rect_stations, self.engine.stations[0:1])
        self.assertCountEqual(circle_stations, self.engine.stations[1:3])
        self.assertCountEqual(triangle_stations, self.engine.stations[3:])

    def test_skip_stations_on_same_path(self) -> None:
        self.engine.stations.clear()
        self.engine.stations.extend(
            get_random_stations(5, self.engine.passengers_mediator)
        )
        for station in self.engine.stations:
            station.draw(self.screen)
        self._connect_stations([i for i in range(5)])
        self.engine._passenger_spawner._spawn_passengers()  # pyright: ignore [reportPrivateUsage]
        self.engine._travel_plan_finder.find_travel_plan_for_passengers()  # pyright: ignore [reportPrivateUsage]
        for station in self.engine.stations:
            for passenger in station.passengers:
                assert passenger.travel_plan
                self.assertEqual(len(passenger.travel_plan.node_path), 1)


if __name__ == "__main__":
    unittest.main()
