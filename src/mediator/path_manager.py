import random
from typing import Final, Mapping

from src.config import max_num_metros, max_num_paths
from src.entity import Metro, Passenger, Path, Station
from src.geometry.point import Point
from src.geometry.type import ShapeType
from src.graph.graph_algo import bfs, build_station_nodes_dict
from src.graph.node import Node
from src.graph.skip_intermediate import skip_stations_on_same_path
from src.travel_plan import TravelPlan
from src.type import Color
from src.ui.ui import UI
from src.utils import hue_to_rgb

from .game_components import GameComponents
from .path_being_created import PathBeingCreated
from .path_finder import find_next_path_for_passenger_at_station


class PathManager:
    __slots__ = (
        "_components",
        "max_num_paths",
        "path_colors",
        "path_to_color",
        "max_num_metros",
        "ui",
        "path_being_created",
    )

    def __init__(
        self,
        components: GameComponents,
        ui: UI,
    ):
        self.max_num_paths: Final[int] = max_num_paths
        self.path_to_color: Final[dict[Path, Color]] = {}
        self.path_colors: Final = self._get_initial_path_colors()
        self.max_num_metros: Final = max_num_metros
        self._components: Final = components
        self.ui: Final = ui
        self.path_being_created: PathBeingCreated | None = None

    ######################
    ### public methods ###
    ######################

    def start_path_on_station(self, station: Station) -> None:
        if len(self._components.paths) >= self.max_num_paths:
            return
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
        self._components.paths.append(path)

    def add_station_to_path(self, station: Station) -> None:
        assert self.path_being_created
        self.path_being_created.add_station_to_path(station)
        if self.path_being_created.path.is_looped:
            self._finish_path_creation()

    def end_path_on_station(self, station: Station) -> None:
        assert self.path_being_created
        path = self.path_being_created.path
        # current station de-dupe
        if self.path_being_created.can_end_with(station):
            self._finish_path_creation()
        # loop
        elif self.path_being_created.can_make_loop(station):
            path.set_loop()
            self._finish_path_creation()
        # non-loop
        elif path.stations[0] != station:
            path.add_station(station)
            self._finish_path_creation()
        else:
            self.abort_path_creation()

    def end_path_on_last_station(self) -> None:
        assert self.path_being_created
        last = self.path_being_created.path.stations[-1]
        self.end_path_on_station(last)

    def abort_path_creation(self) -> None:
        assert self.path_being_created
        self._release_color_for_path(self.path_being_created.path)
        self._components.paths.remove(self.path_being_created.path)
        self.path_being_created = None

    def remove_path(self, path: Path) -> None:
        self.ui.path_to_button[path].remove_path()
        for metro in path.metros:
            # TODO: ensure passengers go to valid stations
            for passenger in metro.passengers:
                assert passenger.last_station
                passenger.last_station.passengers.append(passenger)
            self._components.metros.remove(metro)
        self._release_color_for_path(path)
        self._components.paths.remove(path)
        self._assign_paths_to_buttons()
        self.find_travel_plan_for_passengers()

    def find_travel_plan_for_passengers(self) -> None:
        station_nodes_mapping = build_station_nodes_dict(
            self._components.stations, self._components.paths
        )
        for station in self._components.stations:
            for passenger in station.passengers:
                if self._passenger_has_travel_plan(passenger):
                    continue
                self._find_travel_plan_for_passenger(
                    station_nodes_mapping, station, passenger
                )

    def set_temporary_point(self, position: Point) -> None:
        assert self.path_being_created
        self.path_being_created.path.set_temporary_point(position)

    #######################
    ### private methods ###
    #######################

    def _get_initial_path_colors(self) -> dict[Color, bool]:
        path_colors: Final[dict[Color, bool]] = {}
        for i in range(max_num_paths):
            color = hue_to_rgb(i / (max_num_paths + 1))
            path_colors[color] = False  # not taken
        return path_colors

    def _finish_path_creation(self) -> None:
        assert self.path_being_created
        self.path_being_created.path.is_being_created = False
        self.path_being_created.path.remove_temporary_point()
        if len(self._components.metros) < self.max_num_metros:
            metro = Metro()
            self.path_being_created.path.add_metro(metro)
            self._components.metros.append(metro)
        self.path_being_created = None
        self._assign_paths_to_buttons()

    def _assign_paths_to_buttons(self) -> None:
        self.ui.assign_paths_to_buttons(self._components.paths)

    def _release_color_for_path(self, path: Path) -> None:
        self.path_colors[path.color] = False
        del self.path_to_color[path]

    def _passenger_has_travel_plan(self, passenger: Passenger) -> bool:
        return (
            passenger.travel_plan is not None
            and passenger.travel_plan.next_path is not None
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
                passenger.travel_plan = TravelPlan(node_path[1:])
                self._find_next_path_for_passenger_at_station(passenger, station)
                break

        else:
            passenger.travel_plan = TravelPlan([])

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
