import random
from collections.abc import Sequence
from typing import Final, Mapping

from src.entity import Passenger, Station
from src.entity.path.path import Path
from src.geometry.type import ShapeType
from src.graph.graph_algo import bfs, build_station_nodes_dict
from src.graph.node import Node
from src.graph.skip_intermediate import skip_stations_on_same_path
from src.travel_plan import TravelPlan

from .game_components import GameComponents
from .path_finder import find_next_path_for_passenger_at_station

DEBUG = False


class TravelPlanFinder:
    __slots__ = (
        "_components",
        "_station_nodes_mapping",
    )

    def __init__(self, components: GameComponents):
        self._components: Final = components
        self._station_nodes_mapping: Mapping[Station, Node] | None = None

    ######################
    ### public methods ###
    ######################

    def find_travel_plan_for_passengers(self) -> None:
        self._station_nodes_mapping = build_station_nodes_dict(
            self._components.stations, self._components.paths
        )
        for station in self._components.stations:
            if not self._station_is_connected(station):
                continue
            for passenger in station.passengers:
                if _passenger_has_travel_plan_with_next_path(
                    passenger, self._components.paths
                ):
                    continue
                if DEBUG:
                    print(f"Looking for a travel plan for passenger {passenger}")
                self._find_travel_plan_for_passenger(station, passenger)

    #######################
    ### private methods ###
    #######################

    def _station_is_connected(self, station: Station) -> bool:
        return any(station in path.stations for path in self._components.paths)

    def _find_travel_plan_for_passenger(
        self,
        station: Station,
        passenger: Passenger,
    ) -> None:
        assert self._station_nodes_mapping
        possible_dst_stations = self._get_stations_for_shape_type(
            passenger.destination_shape.type
        )

        for possible_dst_station in possible_dst_stations:
            start = self._station_nodes_mapping[station]
            end = self._station_nodes_mapping[possible_dst_station]
            node_path = bfs(start, end)
            if len(node_path) == 0:
                continue

            assert len(node_path) > 1, "The passenger should have already arrived"
            node_path = skip_stations_on_same_path(node_path)
            passenger.travel_plan = TravelPlan(node_path[1:], passenger.num_id)
            self._find_next_path_for_passenger_at_station(passenger, station)
            break

        else:
            travel_plan = TravelPlan([], passenger.num_id)
            if travel_plan != passenger.travel_plan:
                passenger.travel_plan = travel_plan

    def _get_stations_for_shape_type(self, shape_type: ShapeType) -> list[Station]:
        stations = [
            station
            for station in self._components.stations
            if station.shape.type == shape_type
        ]
        random.shuffle(stations)
        return stations

    def _find_next_path_for_passenger_at_station(
        self, passenger: Passenger, station: Station
    ) -> None:
        assert passenger.travel_plan
        find_next_path_for_passenger_at_station(
            self._components.paths, passenger.travel_plan, station
        )


def _passenger_has_travel_plan_with_next_path(
    passenger: Passenger, paths: Sequence[Path]
) -> bool:
    return (
        passenger.travel_plan is not None and passenger.travel_plan.next_path in paths
    )
