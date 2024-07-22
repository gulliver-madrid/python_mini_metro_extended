import unittest
from collections.abc import Sequence
from unittest.mock import create_autospec

import pygame

from src.config import Config, station_color, station_size
from src.entity import Station, get_random_stations
from src.event.mouse import MouseEvent
from src.event.type import MouseEventType
from src.geometry.circle import Circle
from src.geometry.rect import Rect
from src.graph.graph_algo import bfs, build_station_nodes_dict
from src.graph.node import Node
from src.mediator.mediator import Mediator
from src.reactor import UI_Reactor
from src.utils import get_random_color, get_random_position

from test.base_test import BaseTestCase


class TestGraph(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.width, self.height = Config.screen_width, Config.screen_height
        self.screen = create_autospec(pygame.surface.Surface)
        self.position = get_random_position(self.width, self.height)
        self.color = get_random_color()
        self.mediator = Mediator()
        self.reactor = UI_Reactor(self.mediator)
        for station in self.mediator.stations:
            station.draw(self.screen)

    def tearDown(self) -> None:
        super().tearDown()

    def connect_stations(self, station_idx: Sequence[int]) -> None:
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_DOWN,
                self.mediator.stations[station_idx[0]].position,
            )
        )
        for idx in station_idx[1:]:
            self.reactor.react(
                MouseEvent(
                    MouseEventType.MOUSE_MOTION, self.mediator.stations[idx].position
                )
            )
        self.reactor.react(
            MouseEvent(
                MouseEventType.MOUSE_UP,
                self.mediator.stations[station_idx[-1]].position,
            )
        )

    def test_build_station_nodes_dict(self) -> None:
        self.mediator.stations.clear()
        self.mediator.stations.extend(
            [
                Station(
                    Rect(
                        color=station_color,
                        width=station_size,
                        height=station_size,
                    ),
                    get_random_position(self.width, self.height),
                ),
                Station(
                    Circle(
                        color=station_color,
                        radius=round(station_size / 2),
                    ),
                    get_random_position(self.width, self.height),
                ),
            ]
        )
        for station in self.mediator.stations:
            station.draw(self.screen)

        self.connect_stations([0, 1])

        station_nodes_dict = build_station_nodes_dict(
            self.mediator.stations, self.mediator.paths
        )
        self.assertCountEqual(list(station_nodes_dict.keys()), self.mediator.stations)
        for station, node in station_nodes_dict.items():
            self.assertEqual(node.station, station)

    def test_bfs_two_stations(self) -> None:
        self.mediator.stations.clear()
        self.mediator.stations.extend(get_random_stations(2))
        for station in self.mediator.stations:
            station.draw(self.screen)

        self.connect_stations([0, 1])

        station_nodes_dict = build_station_nodes_dict(
            self.mediator.stations, self.mediator.paths
        )
        start_station = self.mediator.stations[0]
        end_station = self.mediator.stations[1]
        start_node = station_nodes_dict[start_station]
        end_node = station_nodes_dict[end_station]
        node_path = bfs(start_node, end_node)
        self.assertSequenceEqual(
            node_path,
            [start_node, end_node],
        )

    def test_bfs_five_stations(self) -> None:
        self.mediator.stations.clear()
        self.mediator.stations.extend(get_random_stations(5))
        for station in self.mediator.stations:
            station.draw(self.screen)

        self.connect_stations([0, 1, 2])
        self.connect_stations([0, 3])

        station_nodes_dict = build_station_nodes_dict(
            self.mediator.stations, self.mediator.paths
        )
        start_node = station_nodes_dict[self.mediator.stations[0]]
        end_node = station_nodes_dict[self.mediator.stations[2]]
        node_path = bfs(start_node, end_node)
        self.assertSequenceEqual(
            node_path,
            [
                Node(self.mediator.stations[0]),
                Node(self.mediator.stations[1]),
                Node(self.mediator.stations[2]),
            ],
        )
        start_node = station_nodes_dict[self.mediator.stations[1]]
        end_node = station_nodes_dict[self.mediator.stations[3]]
        node_path = bfs(start_node, end_node)
        self.assertSequenceEqual(
            node_path,
            [
                Node(self.mediator.stations[1]),
                Node(self.mediator.stations[0]),
                Node(self.mediator.stations[3]),
            ],
        )
        start_node = station_nodes_dict[self.mediator.stations[0]]
        end_node = station_nodes_dict[self.mediator.stations[4]]
        node_path = bfs(start_node, end_node)
        self.assertSequenceEqual(
            node_path,
            [],
        )


if __name__ == "__main__":
    unittest.main()
