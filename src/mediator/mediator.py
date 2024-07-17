from __future__ import annotations

import pprint
import random
import sys
from typing import Dict, Final, List, Mapping

import pygame

from src.config import PassengerSpawningConfig, num_metros, num_paths, num_stations
from src.entity.get_entity import get_random_stations
from src.entity.metro import Metro
from src.entity.passenger import Passenger
from src.entity.path import Path
from src.entity.station import Station
from src.geometry.point import Point
from src.geometry.type import ShapeType
from src.graph.graph_algo import bfs, build_station_nodes_dict
from src.graph.node import Node
from src.graph.skip_intermediate import skip_stations_on_same_path
from src.mediator.impl import (
    MediatorStatus,
    PassengerCreator,
    PassengerSpawning,
    PathBeingCreated,
    TravelPlans,
)
from src.mediator.passenger_mover import PassengerMover
from src.mediator.path_finder import find_next_path_for_passenger_at_station
from src.travel_plan import TravelPlan
from src.type import Color
from src.ui.path_button import PathButton
from src.ui.ui import UI
from src.utils import hue_to_rgb

pp = pprint.PrettyPrinter(indent=4)


class PathManager:
    __slots__ = (
        "_passenger_spawning",
        "num_paths",
        "num_stations",
        "ui",
        "metros",
        "num_metros",
        "paths",
        "passengers",
        "stations",
        "path_colors",
        "path_to_color",
        "path_being_created",
        "travel_plans",
        "_status",
        "_passenger_mover",
        "path_manager",
    )

    def __init__(
        self,
        paths: List[Path],
        num_paths: int,
        path_colors: Dict[Color, bool],
        path_to_color: Dict[Path, Color],
        passengers: List[Passenger],
        stations: List[Station],
        travel_plans: TravelPlans,
        metros: List[Metro],
        num_metros: int,
        status: MediatorStatus,
        ui: UI,
    ):
        self.paths: Final = paths
        self.num_paths: Final[int] = num_paths
        self.path_colors: Dict[Color, bool] = path_colors
        self.path_to_color: Dict[Path, Color] = path_to_color
        self.passengers: Final[List[Passenger]] = passengers
        self.stations: Final = stations
        self.travel_plans: Final = travel_plans
        self.metros: List[Metro] = metros
        self.num_metros: Final = num_metros
        self.ui: Final = ui
        self.path_being_created: PathBeingCreated | None = None
        self._status = status

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

    def _get_stations_for_shape_type(self, shape_type: ShapeType) -> List[Station]:
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


class Mediator:
    __slots__ = (
        "_passenger_spawning",
        "num_paths",
        "num_metros",
        "num_stations",
        "ui",
        "stations",
        "metros",
        "paths",
        "passengers",
        "path_colors",
        "path_to_color",
        "travel_plans",
        "_status",
        "_passenger_mover",
        "path_manager",
    )

    def __init__(self) -> None:
        pygame.font.init()

        # configs
        self._passenger_spawning = PassengerSpawning(
            PassengerSpawningConfig.start_step, PassengerSpawningConfig.interval_step
        )
        self.num_paths: Final[int] = num_paths
        self.num_metros: int = num_metros
        self.num_stations: int = num_stations

        # UI
        self.ui = UI(self.num_paths)

        # entities
        self.stations: Final = get_random_stations(self.num_stations)
        self.metros: Final[List[Metro]] = []
        self.paths: List[Path] = []
        self.passengers: Final[List[Passenger]] = []
        self.path_colors: Dict[Color, bool] = {}
        for i in range(num_paths):
            color = hue_to_rgb(i / (num_paths + 1))
            self.path_colors[color] = False  # not taken
        self.path_to_color: Dict[Path, Color] = {}

        # status
        self.travel_plans: Final[TravelPlans] = {}
        self._status: Final = MediatorStatus(PassengerSpawningConfig.interval_step)

        # passenger mover
        self._passenger_mover = PassengerMover(
            self.paths, self.passengers, self.travel_plans, self._status
        )

        self.path_manager = PathManager(
            self.paths,
            self.num_paths,
            self.path_colors,
            self.path_to_color,
            self.passengers,
            self.stations,
            self.travel_plans,
            self.metros,
            self.num_metros,
            self._status,
            self.ui,
        )

    ######################
    ### public methods ###
    ######################

    def get_containing_entity(self, position: Point) -> Station | PathButton | None:
        for station in self.stations:
            if station.contains(position):
                return station
        return self.ui.get_containing_button(position) or None

    def increment_time(self, dt_ms: int) -> None:
        if self._status.is_paused:
            return

        self._status.increment_time(dt_ms)

        # move metros
        for path in self.paths:
            for metro in path.metros:
                path.move_metro(metro, dt_ms)

        # spawn passengers
        if self._is_passenger_spawn_time():
            self._spawn_passengers()
            self._status.steps_since_last_spawn = 0

        self.path_manager.find_travel_plan_for_passengers()
        self._move_passengers()

    def render(self, screen: pygame.surface.Surface) -> None:
        for idx, path in enumerate(self.paths):
            path_order = idx - round(self.num_paths / 2)
            path.draw(screen, path_order)
        for station in self.stations:
            station.draw(screen)
        for metro in self.metros:
            metro.draw(screen)
        self.ui.render(screen, self._status.score)

    def toggle_pause(self) -> None:
        self._status.is_paused = not self._status.is_paused

    def exit(self) -> None:
        pygame.quit()
        sys.exit()

    @property
    def is_creating_path(self) -> bool:
        return self._status.is_creating_path

    #######################
    ### private methods ###
    #######################

    def _spawn_passengers(self) -> None:
        station_types = self._get_station_shape_types()
        passenger_creator = PassengerCreator(station_types)
        for station in self.stations:
            if not station.has_room():
                continue
            passenger = passenger_creator.create_passenger(station)
            station.add_passenger(passenger)
            self.passengers.append(passenger)

    def _get_station_shape_types(self) -> List[ShapeType]:
        station_shape_types: List[ShapeType] = []
        for station in self.stations:
            if station.shape.type not in station_shape_types:
                station_shape_types.append(station.shape.type)
        return station_shape_types

    def _is_passenger_spawn_time(self) -> bool:
        return self._passenger_spawning.is_passenger_spawn_time(self._status)

    def _move_passengers(self) -> None:
        for metro in self.metros:

            if not metro.current_station:
                continue

            self._passenger_mover.move_passengers(metro)
