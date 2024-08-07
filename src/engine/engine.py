import pprint
import sys
from typing import Final, NoReturn

import pygame

from src.config import Config, num_stations
from src.entity import Passenger, Path, Station, get_random_stations
from src.geometry.point import Point
from src.passengers_mediator import PassengersMediator
from src.ui.path_button import PathButton
from src.ui.ui import UI, get_gui_height, get_main_surface_height

from .game_components import GameComponents
from .game_renderer import GameRenderer
from .passenger_mover import PassengerMover
from .passenger_spawner import PassengerSpawner, TravelPlansMapping
from .path_manager import PathManager
from .status import MediatorStatus

pp = pprint.PrettyPrinter(indent=4)


class Engine:
    __slots__ = (
        "ui",
        "path_manager",
        "showing_debug",
        "game_speed",
        "_components",
        "_passenger_spawner",
        "_passenger_mover",
        "_game_renderer",
        "steps_allowed",
    )

    _gui_height: Final = get_gui_height()
    _main_surface_height: Final = get_main_surface_height()

    def __init__(self) -> None:
        pygame.font.init()
        passengers_mediator = PassengersMediator()

        # components
        self._components: Final = GameComponents(
            paths=[],
            stations=get_random_stations(num_stations, passengers_mediator),
            metros=[],
            status=MediatorStatus(),
            passengers_mediator=passengers_mediator,
        )

        # status
        self.showing_debug = False
        self.game_speed = 1
        self.steps_allowed: int | None = None

        # UI
        self.ui = UI()
        self._game_renderer = GameRenderer(self._components)

        # delegated classes
        self._passenger_spawner = PassengerSpawner(
            self._components,
            Config.passenger_spawning.interval_step,
        )
        self.path_manager = PathManager(
            self._components,
            self.ui,
        )
        self._passenger_mover = PassengerMover(self._components)

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
        self._passenger_spawner.increment_time(dt_ms)

        # is this needed? or is better only to find travel plans when
        # something change (paths)
        self.path_manager.find_travel_plan_for_passengers()
        self._move_passengers()

        self._move_metros(dt_ms)
        self._passenger_spawner.manage_passengers_spawning()
        if self.steps_allowed is not None:
            self.steps_allowed -= 1
            if self.steps_allowed == 0:
                if not self.is_paused:
                    self.toggle_pause()
                    self.steps_allowed = None

    def try_starting_path_edition(self, position: Point) -> None:
        assert not self.path_manager.path_being_created
        self.path_manager.try_starting_path_edition(position)

    def render(self, screen: pygame.surface.Surface) -> None:
        self._game_renderer.render_game(
            screen,
            gui_height=self._gui_height,
            main_surface_height=self._main_surface_height,
            paths=self.paths,
            max_num_paths=self.path_manager.max_num_paths,
            travel_plans=self.travel_plans,
            path_being_edited=self.path_manager.path_being_edited,
            ui=self.ui,
            is_creating_path=self.path_manager.path_being_created is not None,
            ms_until_next_spawn=self._passenger_spawner.ms_until_next_spawn,
            showing_debug=self.showing_debug,
            game_speed=self.game_speed,
        )

    def toggle_pause(self) -> None:
        if self.is_paused:
            self.steps_allowed = None
        if self.path_manager.path_being_edited:
            assert self.is_paused
            return
        self._components.status.is_paused = not self._components.status.is_paused

    def exit(self) -> NoReturn:
        pygame.quit()
        sys.exit()

    @property
    def passengers_mediator(self) -> PassengersMediator:
        return self._components.passengers_mediator

    @property
    def passengers(self) -> list[Passenger]:
        # tests only
        return self._components.passengers

    @property
    def travel_plans(self) -> TravelPlansMapping:
        return {
            passenger: passenger.travel_plan
            for passenger in self._components.passengers
            if passenger.travel_plan
        }

    @property
    def paths(self) -> list[Path]:
        # tests only
        return self._components.paths

    @property
    def stations(self) -> list[Station]:
        # tests only
        return self._components.stations

    @property
    def is_paused(self) -> bool:
        return self._components.status.is_paused

    #######################
    ### private methods ###
    #######################

    def _move_metros(self, dt_ms: int) -> None:
        for path in self.paths:
            for metro in path.metros:
                path.move_metro(metro, dt_ms)

    def _move_passengers(self) -> None:
        for metro in self._components.metros:

            if not metro.current_station:
                continue

            self._passenger_mover.move_passengers(metro)
