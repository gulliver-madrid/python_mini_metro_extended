import random
from typing import Final, Mapping

from src.entity import Passenger, Station
from src.geometry.type import ShapeType
from src.graph.graph_algo import bfs
from src.graph.node import Node
from src.graph.skip_intermediate import skip_stations_on_same_path
from src.travel_plan import TravelPlan

from .game_components import GameComponents
from .path_finder import find_next_path_for_passenger_at_station


class TravelPlanFinder:
    __slots__ = ("_components",)

    def __init__(self, components: GameComponents):
        self._components: Final = components

    ######################
    ### public methods ###
    ######################

    def find_travel_plan_for_passenger(
        self,
        station_nodes_mapping: Mapping[Station, Node],
        station: Station,
        passenger: Passenger,
    ) -> None:
        possible_dst_stations = self._get_stations_for_shape_type(
            passenger.destination_shape.type
        )

        for possible_dst_station in possible_dst_stations:
            start = station_nodes_mapping[station]
            end = station_nodes_mapping[possible_dst_station]
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

    #######################
    ### private methods ###
    #######################

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