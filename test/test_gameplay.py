from collections.abc import Sequence
from typing import Any
from unittest.mock import Mock, create_autospec, patch

import pygame

from src.config import Config
from src.engine.engine import Engine
from src.engine.path_manager import PathManager
from src.entity.get_entity import get_random_stations
from src.event.keyboard import KeyboardEvent
from src.event.mouse import MouseEvent
from src.event.type import KeyboardEventType, MouseEventType
from src.geometry.point import Point
from src.reactor import UI_Reactor
from src.utils import get_random_color, get_random_position

from test.base_test import BaseTestCase


class TestGameplay(BaseTestCase):
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
        self.engine.stations.clear()
        self.engine.stations.extend(
            get_random_stations(n, mediator=self.engine.mediator)
        )

    def connect_stations(self, station_idx: Sequence[int]) -> None:
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_DOWN,
                self.engine.stations[station_idx[0]].position,
            )
        )
        for idx in station_idx[1:]:
            self.reactor.react(
                MouseEvent(
                    MouseEventType.MOUSE_MOTION, self.engine.stations[idx].position
                )
            )
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_UP,
                self.engine.stations[station_idx[-1]].position,
            )
        )

    @patch.object(PathManager, "start_path_on_station", new_callable=Mock)
    def test_react_mouse_down_start_path(self, mock_start_path_on_station: Any) -> None:
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_DOWN,
                self.engine.stations[3].position + Point(1, 1),
            )
        )
        self.engine.path_manager.start_path_on_station.assert_called_once()  # type: ignore

    def test_mouse_down_and_up_at_the_same_point_does_not_create_path(self) -> None:
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_DOWN, Point(-1, -1)))
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_UP, Point(-1, -1)))

        self.assertEqual(len(self.engine.paths), 0)

    def test_mouse_dragged_between_stations_creates_path(self) -> None:
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_DOWN,
                self.engine.stations[0].position + Point(1, 1),
            )
        )
        new_position = self.engine.stations[1].position + Point(2, 2)
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_MOTION, new_position))
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_UP,
                new_position,
            )
        )

        self.assertEqual(len(self.engine.paths), 1)
        self.assertSequenceEqual(
            self.engine.paths[0].stations,
            [self.engine.stations[0], self.engine.stations[1]],
        )

    def test_mouse_dragged_between_non_station_points_does_not_create_path(
        self,
    ) -> None:
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_DOWN, Point(0, 0)))
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_MOTION, Point(2, 2)))
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_UP, Point(0, 1)))

        self.assertEqual(len(self.engine.paths), 0)

    def test_mouse_dragged_between_station_and_non_station_points_does_not_create_path(
        self,
    ) -> None:
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_DOWN,
                self.engine.stations[0].position + Point(1, 1),
            )
        )
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_MOTION, Point(2, 2)))
        self.reactor.react(MouseEvent(MouseEventType.MOUSE_UP, Point(0, 1)))

        self.assertEqual(len(self.engine.paths), 0)

    def test_mouse_dragged_between_3_stations_creates_looped_path(self) -> None:
        self.connect_stations([0, 1, 2, 0])

        self.assertEqual(len(self.engine.paths), 1)
        self.assertTrue(self.engine.paths[0].is_looped)

    def test_mouse_dragged_between_4_stations_creates_looped_path(self) -> None:
        self.connect_stations([0, 1, 2, 3, 0])
        self.assertEqual(len(self.engine.paths), 1)
        self.assertTrue(self.engine.paths[0].is_looped)

    def test_path_between_2_stations_is_not_looped(self) -> None:
        self.connect_stations([0, 1])
        self.assertEqual(len(self.engine.paths), 1)
        self.assertFalse(self.engine.paths[0].is_looped)

    def test_mouse_dragged_between_3_stations_without_coming_back_to_first_does_not_create_loop(
        self,
    ) -> None:
        self.connect_stations([0, 1, 2])
        self.assertEqual(len(self.engine.paths), 1)
        self.assertFalse(self.engine.paths[0].is_looped)

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
        for station in self.engine.stations:
            station.draw(self.screen)
        self.connect_stations([0, 1])
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(self.engine.paths), 0)
        self.assertEqual(len(self.engine.ui.path_to_button.items()), 0)

    def test_path_buttons_get_assigned_upon_path_creation(self) -> None:
        self._replace_with_random_stations(5)
        for station in self.engine.stations:
            station.draw(self.screen)
        self.connect_stations([0, 1])
        self.assertEqual(len(self.engine.ui.path_to_button.items()), 1)
        self.assertIn(self.engine.paths[0], self.engine.ui.path_to_button)
        self.connect_stations([2, 3])
        self.assertEqual(len(self.engine.ui.path_to_button.items()), 2)
        self.assertIn(self.engine.paths[0], self.engine.ui.path_to_button)
        self.assertIn(self.engine.paths[1], self.engine.ui.path_to_button)
        self.connect_stations([1, 3])
        self.assertEqual(len(self.engine.ui.path_to_button.items()), 3)
        self.assertIn(self.engine.paths[0], self.engine.ui.path_to_button)
        self.assertIn(self.engine.paths[1], self.engine.ui.path_to_button)
        self.assertIn(self.engine.paths[2], self.engine.ui.path_to_button)

    def test_more_paths_can_be_created_after_removing_paths(self) -> None:
        self._replace_with_random_stations(5)
        for station in self.engine.stations:
            station.draw(self.screen)
        self.connect_stations([0, 1])
        self.connect_stations([2, 3])
        self.connect_stations([1, 4])
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(self.engine.paths), 2)
        self.connect_stations([1, 3])
        self.assertEqual(len(self.engine.paths), 3)

    def test_assigned_path_buttons_bubble_to_left(self) -> None:
        self._replace_with_random_stations(5)

        for station in self.engine.stations:
            station.draw(self.screen)
        self.connect_stations([0, 1])
        self.connect_stations([2, 3])
        self.connect_stations([1, 4])
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(self.engine.paths), 2)
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(self.engine.paths), 1)
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(self.engine.paths), 0)

    def test_unassigned_path_buttons_do_nothing_on_click(self) -> None:
        self.assertEqual(len(self.engine.paths), 0)
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(self.engine.paths), 0)
        self.reactor.react(
            MouseEvent(MouseEventType.MOUSE_UP, self.engine.ui.path_buttons[0].position)
        )
        self.assertEqual(len(self.engine.paths), 0)
