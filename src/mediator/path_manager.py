import random
from typing import Final, Mapping

from src.config import num_metros, num_paths
from src.entity.metro import Metro
from src.entity.passenger import Passenger
from src.entity.path import Path
from src.entity.station import Station
from src.geometry.type import ShapeType
from src.graph.graph_algo import bfs, build_station_nodes_dict
from src.graph.node import Node
from src.graph.skip_intermediate import skip_stations_on_same_path
from src.travel_plan import TravelPlan
from src.type import Color
from src.ui.ui import UI
from src.utils import hue_to_rgb

from .impl import MediatorStatus, PathBeingCreated, TravelPlans
from .path_finder import find_next_path_for_passenger_at_station


class PathManager:
    __slots__ = (
        "paths",
        "num_paths",
        "passengers",
        "path_colors",
        "path_to_color",
        "metros",
        "num_metros",
        "stations",
        "travel_plans",
        "ui",
        "path_being_created",
        "_status",
    )

    def __init__(
        self,
        passengers: list[Passenger],
        stations: list[Station],
        travel_plans: TravelPlans,
        metros: list[Metro],
        status: MediatorStatus,
        ui: UI,
    ):
        self.paths: Final[list[Path]] = []
        self.num_paths: Final[int] = num_paths
        self.passengers: Final = passengers
        self.path_to_color: Final[dict[Path, Color]] = {}
        self.path_colors: Final = self._get_initial_path_colors()
        self.metros: Final = metros
        self.num_metros: Final = num_metros
        self.stations: Final = stations
        self.travel_plans: Final = travel_plans
        self.ui: Final = ui
        self.path_being_created: PathBeingCreated | None = None
        self._status: Final = status

    def start_path_on_station(self, station: Station) -> None:
        if len(self.paths) >= self.num_paths:
            return
        self._status.is_creating_path = True
        assigned_color = (0, 0, 0)
        for path_color, taken in self.path_colors.items():
            if taken:
                continue
            assigned_color = path_color
            self.path_colors[path_color] = True
            break
        path = Path(assigned_color)
        self.path_to_color[path] = assigned_color
        path.add_station(station)
        path.is_being_created = True
        self.path_being_created = PathBeingCreated(path)
        self.paths.append(path)

    def add_station_to_path(self, station: Station) -> None:
        assert self.path_being_created is not None
        self.path_being_created.add_station_to_path(station)

    def end_path_on_station(self, station: Station) -> None:
        assert self.path_being_created is not None
        # current station de-dupe
        if self.path_being_created.can_end_with(station):
            self._finish_path_creation()
        # loop
        elif self.path_being_created.can_make_loop(station):
            self.path_being_created.path.set_loop()
            self._finish_path_creation()
        # non-loop
        elif self.path_being_created.path.stations[0] != station:
            self.path_being_created.path.add_station(station)
            self._finish_path_creation()
        else:
            self.abort_path_creation()

    def abort_path_creation(self) -> None:
        assert self.path_being_created is not None
        self._status.is_creating_path = False
        self._release_color_for_path(self.path_being_created.path)
        self.paths.remove(self.path_being_created.path)
        self.path_being_created = None

    def remove_path(self, path: Path) -> None:
        self.ui.path_to_button[path].remove_path()
        for metro in path.metros:
            for passenger in metro.passengers:
                self.passengers.remove(passenger)
            self.metros.remove(metro)
        self._release_color_for_path(path)
        self.paths.remove(path)
        self._assign_paths_to_buttons()
        self.find_travel_plan_for_passengers()

    def find_travel_plan_for_passengers(self) -> None:
        station_nodes_mapping = build_station_nodes_dict(self.stations, self.paths)
        for station in self.stations:
            for passenger in station.passengers:
                if self._passenger_has_travel_plan(passenger):
                    continue
                self._find_travel_plan_for_passenger(
                    station_nodes_mapping, station, passenger
                )

    def _get_initial_path_colors(self) -> dict[Color, bool]:
        path_colors: Final[dict[Color, bool]] = {}
        for i in range(num_paths):
            color = hue_to_rgb(i / (num_paths + 1))
            path_colors[color] = False  # not taken
        return path_colors

    def _finish_path_creation(self) -> None:
        assert self.path_being_created is not None
        self._status.is_creating_path = False
        self.path_being_created.path.is_being_created = False
        self.path_being_created.path.remove_temporary_point()
        if len(self.metros) < self.num_metros:
            metro = Metro()
            self.path_being_created.path.add_metro(metro)
            self.metros.append(metro)
        self.path_being_created = None
        self._assign_paths_to_buttons()

    def _assign_paths_to_buttons(self) -> None:
        self.ui.assign_paths_to_buttons(self.paths)

    def _release_color_for_path(self, path: Path) -> None:
        self.path_colors[path.color] = False
        del self.path_to_color[path]

    def _passenger_has_travel_plan(self, passenger: Passenger) -> bool:
        return (
            passenger in self.travel_plans
            and self.travel_plans[passenger].next_path is not None
        )

    def _find_travel_plan_for_passenger(
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
            if len(node_path) == 1:
                raise RuntimeError("Trying to eliminate from station")
            else:
                assert len(node_path) > 1
                node_path = skip_stations_on_same_path(node_path)
                self.travel_plans[passenger] = TravelPlan(node_path[1:])
                self._find_next_path_for_passenger_at_station(passenger, station)
                break

        else:
            self.travel_plans[passenger] = TravelPlan([])

    def _get_stations_for_shape_type(self, shape_type: ShapeType) -> list[Station]:
        stations = [
            station for station in self.stations if station.shape.type == shape_type
        ]
        random.shuffle(stations)
        return stations

    def _find_next_path_for_passenger_at_station(
        self, passenger: Passenger, station: Station
    ) -> None:
        find_next_path_for_passenger_at_station(
            self.paths, self.travel_plans[passenger], station
        )
