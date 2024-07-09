from __future__ import annotations

import pprint
import random
import sys
from typing import Dict, List, Mapping, Sequence

import pygame

from src.config import (
    num_metros,
    num_paths,
    num_stations,
    passenger_color,
    passenger_size,
    passenger_spawning_interval_step,
    passenger_spawning_start_step,
    score_display_coords,
    score_font_size,
)
from src.entity.get_entity import get_random_stations
from src.entity.metro import Metro
from src.entity.passenger import Passenger
from src.entity.path import Path
from src.entity.station import Station
from src.event.event import Event
from src.event.keyboard import KeyboardEvent
from src.event.mouse import MouseEvent
from src.event.type import KeyboardEventType, MouseEventType
from src.geometry.point import Point
from src.geometry.type import ShapeType
from src.graph.graph_algo import bfs, build_station_nodes_dict
from src.graph.node import Node
from src.travel_plan import TravelPlan
from src.type import Color
from src.ui.button import Button
from src.ui.path_button import PathButton, get_path_buttons
from src.utils import get_shape_from_type, hue_to_rgb

TravelPlans = Dict[Passenger, TravelPlan]
pp = pprint.PrettyPrinter(indent=4)


class Mediator:
    __slots__ = (
        "_passenger_spawning_step",
        "passenger_spawning_interval_step",
        "num_paths",
        "num_metros",
        "num_stations",
        "path_buttons",
        "path_to_button",
        "buttons",
        "font",
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
        self.passenger_spawning_interval_step: int = passenger_spawning_interval_step
        self.num_paths: int = num_paths
        self.num_metros: int = num_metros
        self.num_stations: int = num_stations

        # UI
        self.path_buttons: Sequence[PathButton] = get_path_buttons(self.num_paths)
        self.path_to_button: Dict[Path, PathButton] = {}
        self.buttons = [*self.path_buttons]
        self.font = pygame.font.SysFont("arial", score_font_size)

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

    # public methods

    def render(self, screen: pygame.surface.Surface) -> None:
        for idx, path in enumerate(self.paths):
            path_order = idx - round(self.num_paths / 2)
            path.draw(screen, path_order)
        for station in self.stations:
            station.draw(screen)
        for metro in self.metros:
            metro.draw(screen)
        for button in self.buttons:
            button.draw(screen)
        text_surface = self.font.render(f"Score: {self._status.score}", True, (0, 0, 0))
        screen.blit(text_surface, score_display_coords)

    def react(self, event: Event | None) -> None:
        if isinstance(event, MouseEvent):
            self._react_mouse_event(event)
        elif isinstance(event, KeyboardEvent):
            self._react_keyboard_event(event)

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

    # private methods

    @property
    def _is_creating_path(self) -> bool:
        return self._status.is_creating_path

    @property
    def _is_mouse_down(self) -> bool:
        return self._status.is_mouse_down

    def _get_containing_entity(self, position: Point) -> Station | PathButton | None:
        for station in self.stations:
            if station.contains(position):
                return station
        for button in self.buttons:
            if button.contains(position):
                return button
        return None

    def _remove_path(self, path: Path) -> None:
        self.path_to_button[path].remove_path()
        for metro in path.metros:
            for passenger in metro.passengers:
                self.passengers.remove(passenger)
            self.metros.remove(metro)
        self._release_color_for_path(path)
        self.paths.remove(path)
        self._assign_paths_to_buttons()
        self._find_travel_plan_for_passengers()

    def _start_path_on_station(self, station: Station) -> None:
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

    def _spawn_passengers(self) -> None:
        for station in self.stations:
            station_types = self._get_station_shape_types()
            other_station_shape_types = [
                x for x in station_types if x != station.shape.type
            ]
            destination_shape_type = random.choice(other_station_shape_types)
            destination_shape = get_shape_from_type(
                destination_shape_type, passenger_color, passenger_size
            )
            passenger = Passenger(destination_shape)
            if station.has_room():
                station.add_passenger(passenger)
                self.passengers.append(passenger)

    def _assign_paths_to_buttons(self) -> None:
        for path_button in self.path_buttons:
            path_button.remove_path()

        self.path_to_button = {}
        for i in range(min(len(self.paths), len(self.path_buttons))):
            path = self.paths[i]
            button = self.path_buttons[i]
            button.assign_path(path)
            self.path_to_button[path] = button

    def _react_mouse_event(self, event: MouseEvent) -> None:
        entity = self._get_containing_entity(event.position)

        if event.event_type == MouseEventType.MOUSE_DOWN:
            self._status.is_mouse_down = True
            if isinstance(entity, Station):
                self._start_path_on_station(entity)

        elif event.event_type == MouseEventType.MOUSE_UP:
            self._status.is_mouse_down = False
            if self._is_creating_path:
                assert self.path_being_created is not None
                if isinstance(entity, Station):
                    self._end_path_on_station(entity)
                else:
                    self._abort_path_creation()
            elif isinstance(entity, PathButton) and entity.path:
                self._remove_path(entity.path)

        elif event.event_type == MouseEventType.MOUSE_MOTION:
            if self._status.is_mouse_down:
                if self._is_creating_path and self.path_being_created:
                    if isinstance(entity, Station):
                        self._add_station_to_path(entity)
                    else:
                        self.path_being_created.set_temporary_point(event.position)
            elif isinstance(entity, Button):
                entity.on_hover()
            else:
                for button in self.buttons:
                    button.on_exit()

    def _react_keyboard_event(self, event: KeyboardEvent) -> None:
        if event.event_type == KeyboardEventType.KEY_UP:
            if event.key == pygame.K_SPACE:
                self._status.is_paused = not self._status.is_paused
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def _abort_path_creation(self) -> None:
        assert self.path_being_created is not None
        self._status.is_creating_path = False
        self._release_color_for_path(self.path_being_created)
        self.paths.remove(self.path_being_created)
        self.path_being_created = None

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

    def _end_path_on_station(self, station: Station) -> None:
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
            self._abort_path_creation()

    def _add_station_to_path(self, station: Station) -> None:
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

    def _get_station_shape_types(self) -> List[ShapeType]:
        station_shape_types: List[ShapeType] = []
        for station in self.stations:
            if station.shape.type not in station_shape_types:
                station_shape_types.append(station.shape.type)
        return station_shape_types

    def _is_passenger_spawn_time(self) -> bool:
        return (self._status.steps == self._passenger_spawning_step) or (
            self._status.steps_since_last_spawn == self.passenger_spawning_interval_step
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
                if (
                    self.travel_plans[passenger].next_path
                    and self.travel_plans[passenger].next_path.id == metro.path_id  # type: ignore
                ):
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
                node_path = self._skip_stations_on_same_path(node_path)
                self.travel_plans[passenger] = TravelPlan(node_path[1:])
                self._find_next_path_for_passenger_at_station(passenger, station)
                break

        else:
            self.travel_plans[passenger] = TravelPlan([])

    def _get_stations_for_shape_type(self, shape_type: ShapeType) -> List[Station]:
        stations: List[Station] = []
        for station in self.stations:
            if station.shape.type == shape_type:
                stations.append(station)
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

    def _skip_stations_on_same_path(self, node_path: List[Node]) -> List[Node]:
        assert len(node_path) >= 2
        if len(node_path) == 2:
            return node_path
        nodes_to_remove: List[Node] = []
        i = 0
        j = 1
        path_set_list = [x.paths for x in node_path]
        path_set_list.append(set())
        while j <= len(path_set_list) - 1:
            set_a = path_set_list[i]
            set_b = path_set_list[j]
            if set_a & set_b:
                j += 1
            else:
                for k in range(i + 1, j - 1):
                    nodes_to_remove.append(node_path[k])
                i = j - 1
                j += 1
        for node in nodes_to_remove:
            node_path.remove(node)
        return node_path

    def _find_shared_path(self, station_a: Station, station_b: Station) -> Path | None:
        for path in self.paths:
            stations = path.stations
            if (station_a in stations) and (station_b in stations):
                return path
        return None


class MediatorStatus:
    __slots__ = (
        "_time_ms",
        "steps",
        "steps_since_last_spawn",
        "is_mouse_down",
        "is_creating_path",
        "is_paused",
        "score",
    )

    def __init__(self, passenger_spawning_interval_step: int) -> None:
        self._time_ms: int = 0
        self.steps: int = 0
        self.steps_since_last_spawn: int = passenger_spawning_interval_step + 1
        self.is_mouse_down: bool = False
        self.is_creating_path: bool = False
        self.is_paused: bool = False
        self.score: int = 0

    def increment_time(self, dt_ms: int) -> None:
        assert not self.is_paused

        self._time_ms += dt_ms
        self.steps += 1
        self.steps_since_last_spawn += 1
