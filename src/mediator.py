from __future__ import annotations

import pprint
import random
import sys
from collections.abc import Sequence
from typing import Dict, Final, List, Mapping

import pygame

from src.config import (
    num_metros,
    num_paths,
    num_stations,
    passenger_color,
    passenger_size,
    passenger_spawning_interval_step,
    passenger_spawning_start_step,
)
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
from src.travel_plan import TravelPlan
from src.type import Color
from src.ui.path_button import PathButton
from src.ui.ui import UI
from src.utils import get_shape_from_type, hue_to_rgb

TravelPlans = Dict[Passenger, TravelPlan]
pp = pprint.PrettyPrinter(indent=4)


class Mediator:
    __slots__ = (
        "_passenger_spawning_step",
        "_passenger_spawning_interval_step",
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
        "path_being_created",
        "travel_plans",
        "_status",
    )

    def __init__(self) -> None:
        pygame.font.init()

        # configs
        self._passenger_spawning_step: int = passenger_spawning_start_step
        self._passenger_spawning_interval_step: int = passenger_spawning_interval_step
        self.num_paths: int = num_paths
        self.num_metros: int = num_metros
        self.num_stations: int = num_stations

        # UI
        self.ui = UI(self.num_paths)

        # entities
        self.stations = get_random_stations(self.num_stations)
        self.metros: List[Metro] = []
        self.paths: List[Path] = []
        self.passengers: List[Passenger] = []
        self.path_colors: Dict[Color, bool] = {}
        for i in range(num_paths):
            color = hue_to_rgb(i / (num_paths + 1))
            self.path_colors[color] = False  # not taken
        self.path_to_color: Dict[Path, Color] = {}

        # status
        self.path_being_created: Path | None = None
        self.travel_plans: TravelPlans = {}
        self._status = MediatorStatus(passenger_spawning_interval_step)

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

        self._find_travel_plan_for_passengers()
        self._move_passengers()

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
        self.path_being_created = path
        self.paths.append(path)

    def add_station_to_path(self, station: Station) -> None:
        assert self.path_being_created is not None
        if self.path_being_created.stations[-1] == station:
            return
        # loop
        if (
            len(self.path_being_created.stations) > 1
            and self.path_being_created.stations[0] == station
        ):
            self.path_being_created.set_loop()
        # non-loop
        elif self.path_being_created.stations[0] != station:
            if self.path_being_created.is_looped:
                self.path_being_created.remove_loop()
            self.path_being_created.add_station(station)

    def abort_path_creation(self) -> None:
        assert self.path_being_created is not None
        self._status.is_creating_path = False
        self._release_color_for_path(self.path_being_created)
        self.paths.remove(self.path_being_created)
        self.path_being_created = None

    def end_path_on_station(self, station: Station) -> None:
        assert self.path_being_created is not None
        # current station de-dupe
        if (
            len(self.path_being_created.stations) > 1
            and self.path_being_created.stations[-1] == station
        ):
            self._finish_path_creation()
        # loop
        elif (
            len(self.path_being_created.stations) > 1
            and self.path_being_created.stations[0] == station
        ):
            self.path_being_created.set_loop()
            self._finish_path_creation()
        # non-loop
        elif self.path_being_created.stations[0] != station:
            self.path_being_created.add_station(station)
            self._finish_path_creation()
        else:
            self.abort_path_creation()

    def remove_path(self, path: Path) -> None:
        self.ui.path_to_button[path].remove_path()
        for metro in path.metros:
            for passenger in metro.passengers:
                self.passengers.remove(passenger)
            self.metros.remove(metro)
        self._release_color_for_path(path)
        self.paths.remove(path)
        self._assign_paths_to_buttons()
        self._find_travel_plan_for_passengers()

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
        shape_types_to_others: Final[Mapping[ShapeType, Sequence[ShapeType]]] = {
            shape_type: [x for x in station_types if x != shape_type]
            for shape_type in set(station_types)
        }

        def create_passenger(station: Station) -> Passenger:
            other_shape_types = shape_types_to_others[station.shape.type]
            destination_shape_type = random.choice(other_shape_types)
            destination_shape = get_shape_from_type(
                destination_shape_type, passenger_color, passenger_size
            )
            return Passenger(destination_shape)

        for station in self.stations:
            if not station.has_room():
                continue
            passenger = create_passenger(station)
            station.add_passenger(passenger)
            self.passengers.append(passenger)

    def _assign_paths_to_buttons(self) -> None:
        self.ui.assign_paths_to_buttons(self.paths)

    def _release_color_for_path(self, path: Path) -> None:
        self.path_colors[path.color] = False
        del self.path_to_color[path]

    def _finish_path_creation(self) -> None:
        assert self.path_being_created is not None
        self._status.is_creating_path = False
        self.path_being_created.is_being_created = False
        self.path_being_created.remove_temporary_point()
        if len(self.metros) < self.num_metros:
            metro = Metro()
            self.path_being_created.add_metro(metro)
            self.metros.append(metro)
        self.path_being_created = None
        self._assign_paths_to_buttons()

    def _get_station_shape_types(self) -> List[ShapeType]:
        station_shape_types: List[ShapeType] = []
        for station in self.stations:
            if station.shape.type not in station_shape_types:
                station_shape_types.append(station.shape.type)
        return station_shape_types

    def _is_passenger_spawn_time(self) -> bool:
        return (self._status.steps == self._passenger_spawning_step) or (
            self._status.steps_since_last_spawn
            == self._passenger_spawning_interval_step
        )

    def _move_passengers(self) -> None:
        for metro in self.metros:

            if not metro.current_station:
                continue

            passengers_to_remove: List[Passenger] = []
            passengers_from_metro_to_station: List[Passenger] = []
            passengers_from_station_to_metro: List[Passenger] = []

            # queue
            for passenger in metro.passengers:
                if metro.current_station.shape.type == passenger.destination_shape.type:
                    passengers_to_remove.append(passenger)
                elif (
                    self.travel_plans[passenger].get_next_station()
                    == metro.current_station
                ):
                    passengers_from_metro_to_station.append(passenger)
            for passenger in metro.current_station.passengers:
                next_path = self.travel_plans[passenger].next_path
                if next_path and next_path.id == metro.path_id:
                    passengers_from_station_to_metro.append(passenger)

            # process
            for passenger in passengers_to_remove:
                passenger.is_at_destination = True
                metro.remove_passenger(passenger)
                self.passengers.remove(passenger)
                del self.travel_plans[passenger]
                self._status.score += 1

            for passenger in passengers_from_metro_to_station:
                if not metro.current_station.has_room():
                    continue
                metro.move_passenger(passenger, metro.current_station)
                self.travel_plans[passenger].increment_next_station()
                self._find_next_path_for_passenger_at_station(
                    passenger, metro.current_station
                )

            for passenger in passengers_from_station_to_metro:
                if metro.has_room():
                    metro.current_station.move_passenger(passenger, metro)

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
                # passenger arrived at destination
                station.remove_passenger(passenger)
                self.passengers.remove(passenger)
                passenger.is_at_destination = True
                del self.travel_plans[passenger]
                break
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

    def _find_travel_plan_for_passengers(self) -> None:
        station_nodes_mapping = build_station_nodes_dict(self.stations, self.paths)
        for station in self.stations:
            for passenger in station.passengers:
                if self._passenger_has_travel_plan(passenger):
                    continue
                self._find_travel_plan_for_passenger(
                    station_nodes_mapping, station, passenger
                )

    def _find_next_path_for_passenger_at_station(
        self, passenger: Passenger, station: Station
    ) -> None:
        next_station = self.travel_plans[passenger].get_next_station()
        assert next_station is not None
        next_path = self._find_shared_path(station, next_station)
        self.travel_plans[passenger].next_path = next_path

    def _find_shared_path(self, station_a: Station, station_b: Station) -> Path | None:
        """Returns the first path both stations belong to, or None if there is no shared path"""
        for path in self.paths:
            if all(station in path.stations for station in (station_a, station_b)):
                return path
        return None


class MediatorStatus:
    __slots__ = (
        "_time_ms",
        "steps",
        "steps_since_last_spawn",
        "is_creating_path",
        "is_paused",
        "score",
    )

    def __init__(self, passenger_spawning_interval_step: int) -> None:
        self._time_ms: int = 0
        self.steps: int = 0
        self.steps_since_last_spawn: int = passenger_spawning_interval_step + 1
        self.is_creating_path: bool = False
        self.is_paused: bool = False
        self.score: int = 0

    def increment_time(self, dt_ms: int) -> None:
        assert not self.is_paused

        self._time_ms += dt_ms
        self.steps += 1
        self.steps_since_last_spawn += 1
