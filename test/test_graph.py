import unittest
from unittest.mock import create_autospec

import pygame

from src.config import Config, station_color, station_size
from src.engine.engine import Engine
from src.entity import Station, get_random_stations
from src.geometry.circle import Circle
from src.geometry.polygons import Rect
from src.graph.graph_algo import bfs, build_station_nodes_dict
from src.graph.node import Node
from src.reactor import UI_Reactor
from src.utils import get_random_color, get_random_position

from test.base_test import GameplayBaseTestCase
from test.legacy_access import (
    legacy_get_engine_passengers_mediator,
    legacy_get_engine_paths,
    legacy_get_engine_stations,
)


class TestGraph(GameplayBaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.width, self.height = Config.screen_width, Config.screen_height
        self.screen = create_autospec(pygame.surface.Surface)
        self.position = get_random_position(self.width, self.height)
        self.color = get_random_color()
        self.engine = Engine()
        self.reactor = UI_Reactor(self.engine)
        for station in legacy_get_engine_stations(self.engine):
            station.draw(self.screen)

    def tearDown(self) -> None:
        super().tearDown()

    def _replace_with_random_stations(self, n: int) -> None:
        self._replace_stations(
            get_random_stations(
                n,
                passengers_mediator=legacy_get_engine_passengers_mediator(self.engine),
            )
        )

    def test_build_station_nodes_dict(self) -> None:
        self._replace_stations(
            [
                Station(
                    Rect(
                        color=station_color,
                        width=station_size,
                        height=station_size,
                    ),
                    get_random_position(self.width, self.height),
                    legacy_get_engine_passengers_mediator(self.engine),
                ),
                Station(
                    Circle(
                        color=station_color,
                        radius=round(station_size / 2),
                    ),
                    get_random_position(self.width, self.height),
                    legacy_get_engine_passengers_mediator(self.engine),
                ),
            ]
        )
        for station in legacy_get_engine_stations(self.engine):
            station.draw(self.screen)

        self._connect_stations([0, 1])

        station_nodes_dict = build_station_nodes_dict(
            legacy_get_engine_stations(self.engine),
            legacy_get_engine_paths(self.engine),
        )
        self.assertCountEqual(
            list(station_nodes_dict.keys()), legacy_get_engine_stations(self.engine)
        )
        for station, node in station_nodes_dict.items():
            self.assertEqual(node.station, station)

    def test_bfs_two_stations(self) -> None:
        self._replace_with_random_stations(2)
        for station in legacy_get_engine_stations(self.engine):
            station.draw(self.screen)

        self._connect_stations([0, 1])

        station_nodes_dict = build_station_nodes_dict(
            legacy_get_engine_stations(self.engine),
            legacy_get_engine_paths(self.engine),
        )
        start_station = legacy_get_engine_stations(self.engine)[0]
        end_station = legacy_get_engine_stations(self.engine)[1]
        start_node = station_nodes_dict[start_station]
        end_node = station_nodes_dict[end_station]
        node_path = bfs(start_node, end_node)
        self.assertSequenceEqual(
            node_path,
            [start_node, end_node],
        )

    def test_bfs_five_stations(self) -> None:
        self._replace_with_random_stations(5)
        for station in legacy_get_engine_stations(self.engine):
            station.draw(self.screen)

        self._connect_stations([0, 1, 2])
        self._connect_stations([0, 3])

        station_nodes_dict = build_station_nodes_dict(
            legacy_get_engine_stations(self.engine),
            legacy_get_engine_paths(self.engine),
        )
        start_node = station_nodes_dict[legacy_get_engine_stations(self.engine)[0]]
        end_node = station_nodes_dict[legacy_get_engine_stations(self.engine)[2]]
        node_path = bfs(start_node, end_node)
        self.assertSequenceEqual(
            node_path,
            [
                Node(legacy_get_engine_stations(self.engine)[0]),
                Node(legacy_get_engine_stations(self.engine)[1]),
                Node(legacy_get_engine_stations(self.engine)[2]),
            ],
        )
        start_node = station_nodes_dict[legacy_get_engine_stations(self.engine)[1]]
        end_node = station_nodes_dict[legacy_get_engine_stations(self.engine)[3]]
        node_path = bfs(start_node, end_node)
        self.assertSequenceEqual(
            node_path,
            [
                Node(legacy_get_engine_stations(self.engine)[1]),
                Node(legacy_get_engine_stations(self.engine)[0]),
                Node(legacy_get_engine_stations(self.engine)[3]),
            ],
        )
        start_node = station_nodes_dict[legacy_get_engine_stations(self.engine)[0]]
        end_node = station_nodes_dict[legacy_get_engine_stations(self.engine)[4]]
        node_path = bfs(start_node, end_node)
        self.assertSequenceEqual(
            node_path,
            [],
        )


if __name__ == "__main__":
    unittest.main()
