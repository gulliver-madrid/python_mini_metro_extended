import pprint
import sys
from typing import Final, NoReturn

import pygame

from src.config import Config, num_stations
from src.entity.get_entity import get_random_stations
from src.entity.passenger import Passenger
from src.entity.path import Path
from src.entity.station import Station
from src.geometry.point import Point
from src.geometry.type import ShapeType
from src.mediator.game_components import GameComponents
from src.ui.path_button import PathButton
from src.ui.ui import UI, get_gui_height, get_main_surface_height

from .game_renderer import GameRenderer
from .impl import MediatorStatus, PassengerSpawning, TravelPlansMapping
from .passenger_creator import PassengerCreator
from .passenger_mover import PassengerMover
from .path_manager import PathManager

pp = pprint.PrettyPrinter(indent=4)


class Mediator:
    __slots__ = (
        "_components",
        "_passenger_spawning",
        "num_stations",
        "ui",
        "path_manager",
        "_passenger_mover",
        "showing_debug",
        "game_speed",
        "_game_renderer",
    )

    _gui_height: Final = get_gui_height()
    _main_surface_height: Final = get_main_surface_height()

    def __init__(self) -> None:
        pygame.font.init()

        # configs
        self._passenger_spawning = PassengerSpawning(
            Config.passenger_spawning.interval_step,
        )
        self.num_stations: int = num_stations

        # components
        self._components: Final = GameComponents(
            stations=get_random_stations(self.num_stations),
            metros=[],
            status=MediatorStatus(),
        )

        # status
        self.showing_debug = False
        self.game_speed = 1

        # UI
        self.ui = UI()
        self._game_renderer = GameRenderer()

        # delegated classes
        self.path_manager = PathManager(
            self._components,
            self.ui,
        )
        self._passenger_mover = PassengerMover(
            self.path_manager.paths, self._components.status
        )

        self.ui.init(self.path_manager.max_num_paths)

    ######################
    ### public methods ###
    ######################

    def set_clock(self, clock: pygame.time.Clock) -> None:
        self.ui.clock = clock

    def get_containing_entity(self, position: Point) -> Station | PathButton | None:
        for station in self._components.stations:
            if station.contains(position):
                return station
        return self.ui.get_containing_button(position) or None

    def increment_time(self, dt_ms: int) -> None:
        if self._components.status.is_paused:
            return

        dt_ms *= self.game_speed
        self._passenger_spawning.increment_time(dt_ms)

        self._move_metros(dt_ms)
        self._manage_passengers_spawning()

        self.path_manager.find_travel_plan_for_passengers()
        self._move_passengers()

    def _move_metros(self, dt_ms: int) -> None:
        for path in self.paths:
            for metro in path.metros:
                path.move_metro(metro, dt_ms)

    def _manage_passengers_spawning(self) -> None:
        if self._is_passenger_spawn_time():
            self._spawn_passengers()
            self._passenger_spawning.reset()

    def render(self, screen: pygame.surface.Surface) -> None:
        self._game_renderer.render_game(
            screen,
            gui_height=self._gui_height,
            main_surface_height=self._main_surface_height,
            components=self._components,
            paths=self.paths,
            max_num_paths=self.path_manager.max_num_paths,
            passengers=self.passengers,
            travel_plans=self.travel_plans,
            ui=self.ui,
            ms_until_next_spawn=self._passenger_spawning.ms_until_next_spawn,
            showing_debug=self.showing_debug,
            game_speed=self.game_speed,
        )

    def toggle_pause(self) -> None:
        self._components.status.is_paused = not self._components.status.is_paused

    def exit(self) -> NoReturn:
        pygame.quit()
        sys.exit()

    @property
    def passengers(self) -> list[Passenger]:
        passengers: list[Passenger] = []
        for metro in self._components.metros:
            passengers.extend(metro.passengers)

        for station in self._components.stations:
            passengers.extend(station.passengers)
        return passengers

    @property
    def travel_plans(self) -> TravelPlansMapping:
        return {
            passenger: passenger.travel_plan
            for passenger in self.passengers
            if passenger.travel_plan
        }

    @property
    def paths(self) -> list[Path]:
        # tests only
        return self.path_manager.paths

    @property
    def stations(self) -> list[Station]:
        # tests only
        return self._components.stations

    @property
    def is_creating_path(self) -> bool:
        return self._components.status.is_creating_path

    @property
    def is_paused(self) -> bool:
        return self._components.status.is_paused

    #######################
    ### private methods ###
    #######################

    def _spawn_passengers(self) -> None:
        station_types = self._get_station_shape_types()
        passenger_creator = PassengerCreator(station_types)
        for station in self._components.stations:
            if not station.has_room():
                continue
            passenger = passenger_creator.create_passenger(station)
            station.add_passenger(passenger)

    def _get_station_shape_types(self) -> list[ShapeType]:
        station_shape_types: list[ShapeType] = []
        for station in self._components.stations:
            if station.shape.type not in station_shape_types:
                station_shape_types.append(station.shape.type)
        return station_shape_types

    def _is_passenger_spawn_time(self) -> bool:
        return self._passenger_spawning.is_passenger_spawn_time(self._components.status)

    def _move_passengers(self) -> None:
        for metro in self._components.metros:

            if not metro.current_station:
                continue

            self._passenger_mover.move_passengers(metro)
