from math import ceil
from typing import Any, Final
from unittest.mock import create_autospec, patch

import pygame

from src.config import Config
from src.engine.engine import Engine
from src.engine.path_edition import EditingIntermediateStations
from src.engine.path_manager import PathManager
from src.entity.get_entity import get_random_stations
from src.entity.segments import PathSegment
from src.event.keyboard import KeyboardEvent
from src.event.mouse import MouseEvent
from src.event.type import KeyboardEventType, MouseEventType
from src.geometry.point import Point
from src.reactor import UI_Reactor
from src.utils import get_random_color, get_random_position

from test.base_test import GameplayBaseTestCase
from test.legacy_access import (
    legacy_get_engine_passengers_mediator,
    legacy_get_engine_paths,
    legacy_get_engine_stations,
    legacy_path_segments,
)


class TestGameplay(GameplayBaseTestCase):
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

    def _replace_with_random_stations(self, n: int) -> None:
        self._replace_stations(
            get_random_stations(
                n,
                passengers_mediator=legacy_get_engine_passengers_mediator(self.engine),
            )
        )

    @patch.object(PathManager, "start_path_on_station", return_value=iter([None]))
    def test_react_mouse_down_start_path(self, mock_start_path_on_station: Any) -> None:
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_DOWN,
                legacy_get_engine_stations(self.engine)[3].position + Point(1, 1),
            )
        )
        mock_start_path_on_station.assert_called_once()

    def test_mouse_down_and_up_at_the_same_point_does_not_create_path(self) -> None:
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_DOWN, Point(-1, -1)))
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_UP, Point(-1, -1)))

        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 0)

    def test_mouse_dragged_between_stations_creates_path(self) -> None:
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_DOWN,
                legacy_get_engine_stations(self.engine)[0].position + Point(1, 1),
            )
        )
        new_position = legacy_get_engine_stations(self.engine)[1].position + Point(2, 2)
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_MOTION, new_position))
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_UP,
                new_position,
            )
        )

        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 1)
        self.assertSequenceEqual(
            legacy_get_engine_paths(self.engine)[0].stations,
            [
                legacy_get_engine_stations(self.engine)[0],
                legacy_get_engine_stations(self.engine)[1],
            ],
        )

    def test_mouse_dragged_between_non_station_points_does_not_create_path(
        self,
    ) -> None:
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_DOWN, Point(0, 0)))
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_MOTION, Point(2, 2)))
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_UP, Point(0, 1)))

        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 0)

    def test_mouse_dragged_between_station_and_non_station_points_does_not_create_path(
        self,
    ) -> None:
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_DOWN,
                legacy_get_engine_stations(self.engine)[0].position + Point(1, 1),
            )
        )
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_MOTION, Point(2, 2)))
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_UP, Point(0, 1)))

        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 0)

    def test_mouse_dragged_between_3_stations_creates_looped_path(self) -> None:
        self._connect_stations([0, 1, 2, 0])

        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 1)
        self.assertTrue(legacy_get_engine_paths(self.engine)[0].is_looped)

    def test_mouse_dragged_between_4_stations_creates_looped_path(self) -> None:
        self._connect_stations([0, 1, 2, 3, 0])
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 1)
        self.assertTrue(legacy_get_engine_paths(self.engine)[0].is_looped)

    def test_path_between_2_stations_is_not_looped(self) -> None:
        self._connect_stations([0, 1])
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 1)
        self.assertFalse(legacy_get_engine_paths(self.engine)[0].is_looped)

    def test_mouse_dragged_between_3_stations_without_coming_back_to_first_does_not_create_loop(
        self,
    ) -> None:
        self._connect_stations([0, 1, 2])
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 1)
        self.assertFalse(legacy_get_engine_paths(self.engine)[0].is_looped)

    def test_space_key_pauses_and_unpauses_game(self) -> None:
        self.reactor.react(KeyboardEvent(KeyboardEventType.KEY_DOWN, pygame.K_SPACE))

        self.assertTrue(
            self.engine._components.status.is_paused  # pyright: ignore [reportPrivateUsage]
        )

        self.reactor.react(KeyboardEvent(KeyboardEventType.KEY_DOWN, pygame.K_SPACE))

        self.assertFalse(
            self.engine._components.status.is_paused  # pyright: ignore [reportPrivateUsage]
        )

    def test_path_button_removes_path_on_click(self) -> None:
        self._replace_with_random_stations(5)
        for station in legacy_get_engine_stations(self.engine):
            station.draw(self.screen)
        self._connect_stations([0, 1])
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 0)
        self.assertEqual(len(self.engine.ui.path_to_button.items()), 0)

    def test_path_buttons_get_assigned_upon_path_creation(self) -> None:
        self._replace_with_random_stations(5)
        for station in legacy_get_engine_stations(self.engine):
            station.draw(self.screen)
        self._connect_stations([0, 1])
        self.assertEqual(len(self.engine.ui.path_to_button.items()), 1)
        self.assertIn(
            legacy_get_engine_paths(self.engine)[0], self.engine.ui.path_to_button
        )
        self._connect_stations([2, 3])
        self.assertEqual(len(self.engine.ui.path_to_button.items()), 2)
        self.assertIn(
            legacy_get_engine_paths(self.engine)[0], self.engine.ui.path_to_button
        )
        self.assertIn(
            legacy_get_engine_paths(self.engine)[1], self.engine.ui.path_to_button
        )
        self._connect_stations([1, 3])
        self.assertEqual(len(self.engine.ui.path_to_button.items()), 3)
        self.assertIn(
            legacy_get_engine_paths(self.engine)[0], self.engine.ui.path_to_button
        )
        self.assertIn(
            legacy_get_engine_paths(self.engine)[1], self.engine.ui.path_to_button
        )
        self.assertIn(
            legacy_get_engine_paths(self.engine)[2], self.engine.ui.path_to_button
        )

    def test_more_paths_can_be_created_after_removing_paths(self) -> None:
        self._replace_with_random_stations(5)
        for station in legacy_get_engine_stations(self.engine):
            station.draw(self.screen)
        self._connect_stations([0, 1])
        self._connect_stations([2, 3])
        self._connect_stations([1, 4])
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 2)
        self._connect_stations([1, 3])
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 3)

    def test_assigned_path_buttons_bubble_to_left(self) -> None:
        self._replace_with_random_stations(5)

        for station in legacy_get_engine_stations(self.engine):
            station.draw(self.screen)
        self._connect_stations([0, 1])
        self._connect_stations([2, 3])
        self._connect_stations([1, 4])
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 2)
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 1)
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 0)

    def test_unassigned_path_buttons_do_nothing_on_click(self) -> None:
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 0)
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 0)
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(legacy_get_engine_paths(self.engine)), 0)

    def test_the_program_doesnt_break_if_mouse_motion_is_skipped(self) -> None:
        """
        Tests that if pygame deliver a mouse click event without a previous mouse movement
        to that position, the program doesn't break.
        """

        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_DOWN,
                legacy_get_engine_stations(self.engine)[0].position,
            )
        )
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_UP,
                legacy_get_engine_stations(self.engine)[1].position,
            )
        )

    def test_that_removing_the_initial_station_doesnt_cause_list_index_out_of_range_if_metro_is_in_the_last_segment(
        self,
    ) -> None:
        framerate: Final = 60
        dt_ms: Final = ceil(1000 / framerate)
        self._connect_stations([0, 1, 2, 3])
        metros = self.engine._components.metros  # pyright: ignore [reportPrivateUsage]
        paths = legacy_get_engine_paths(self.engine)
        assert len(metros) == 1
        assert len(paths) == 1
        metro = metros[0]
        path = paths[0]
        # run until the train is in the last segment
        while True:
            self.engine.increment_time(dt_ms)
            assert metro.travel_step
            if metro.travel_step.current == legacy_path_segments(path)[-1]:
                break
        first = legacy_path_segments(path)[0]
        assert isinstance(first, PathSegment)

        # remove first station
        editing = EditingIntermediateStations(path, first)
        editing.remove_station(legacy_get_engine_stations(self.engine)[0])

        # resume running (the bug raised here)
        while metro.is_forward:
            self.engine.increment_time(dt_ms)

        # removing was ok
        assert len(path.stations) == 3

    def test_expanding_path(self) -> None:
        """Test than path can be expanded from the start or from the end"""
        for expansion_start in (0, 1):
            with self.subTest(expansion_start=expansion_start):
                self.setUp()
                try:
                    self._subtest_expanding_path(expansion_start)
                finally:
                    self.tearDown()

    def _subtest_expanding_path(self, expansion_start: int) -> None:
        # Arrange
        paths = self.engine._components.paths  # pyright: ignore [reportPrivateUsage]
        self._connect_stations([0, 1])
        assert len(paths) == 1
        path = paths[0]
        assert len(path.stations) == 2

        expansion_end: Final = 2

        # Act
        # first click is for starting a new path
        self._send_event_to_station(MouseEventType.MOUSE_DOWN, expansion_start)
        self._send_event_to_station(MouseEventType.MOUSE_UP, expansion_start)
        # second click for expanding current path
        self._send_event_to_station(MouseEventType.MOUSE_DOWN, expansion_start)
        # movement to expand: first a small move (realistic human)
        self._send_event_to_station(
            MouseEventType.MOUSE_MOTION, expansion_start, Point(2, 2)
        )
        # after, go to the station target
        self._send_event_to_station(MouseEventType.MOUSE_MOTION, expansion_end)
        # release
        self._send_event_to_station(MouseEventType.MOUSE_UP, expansion_end)

        # Assert
        assert len(paths) == 1
        assert path is paths[0]
        assert len(path.stations) == 3
