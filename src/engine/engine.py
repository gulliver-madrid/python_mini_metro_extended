import pprint
import sys
from typing import Final, NoReturn

import pygame

from src.config import Config
from src.entity import Station, get_random_stations
from src.geometry.point import Point
from src.gui.gui import GUI, get_gui_height, get_main_surface_height
from src.gui.path_button import PathButton
from src.passengers_mediator import PassengersMediator

from .game_components import GameComponents
from .game_renderer import GameRenderer
from .passenger_mover import PassengerMover
from .passenger_spawner import PassengerSpawner, TravelPlansMapping
from .path_manager import PathManager
from .status import EngineStatus
from .travel_plan_finder import TravelPlanFinder

pp = pprint.PrettyPrinter(indent=4)


class Engine:
    __slots__ = (
        "path_manager",
        "showing_debug",
        "game_speed",
        "_components",
        "_passenger_spawner",
        "_passenger_mover",
        "_game_renderer",
        "_travel_plan_finder",
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
            stations=get_random_stations(Config.num_stations, passengers_mediator),
            metros=[],
            status=EngineStatus(),
            passengers_mediator=passengers_mediator,
        )
        self._travel_plan_finder = TravelPlanFinder(self._components)

        # status
        self.showing_debug = False
        self.game_speed = 1
        self.steps_allowed: int | None = None

        # UI
        self._game_renderer = GameRenderer(self._components)

        # delegated classes
        self._passenger_spawner = PassengerSpawner(
            self._components,
            Config.passenger_spawning.interval_step,
        )

        self.path_manager = PathManager(
            self._components,
            self._travel_plan_finder,
        )
        self._passenger_mover = PassengerMover(self._components)

        self._components.gui.init(self.path_manager.max_num_paths)

    ######################
    ### public methods ###
    ######################

    def set_clock(self, clock: pygame.time.Clock) -> None:
        self._components.gui.clock = clock

    def get_containing_entity(self, position: Point) -> Station | PathButton | None:
        for station in self._components.stations:
            if station.contains(position):
                return station
        return self._components.gui.get_containing_button(position) or None

    def increment_time(self, dt_ms: int) -> None:
        if self._components.status.is_paused:
            return

        self._components.status.game_time += 1
        dt_ms *= self.game_speed
        self._passenger_spawner.increment_time(dt_ms)

        # is this needed? or is better only to find travel plans when
        # something change (paths)
        self._travel_plan_finder.find_travel_plan_for_passengers()
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
        self.path_manager.try_starting_path_edition(position)

    def max_paths_reached(self) -> bool:
        return len(self._components.paths) < self.path_manager.max_num_paths

    def render(self, screen: pygame.surface.Surface) -> None:
        self._game_renderer.render_game(
            screen,
            gui_height=self._gui_height,
            main_surface_height=self._main_surface_height,
            paths=self._components.paths,
            travel_plans=self.travel_plans,
            editing_intermediate_stations=self.path_manager.editing_intermediate_stations,
            is_creating_path=bool(self.path_manager.is_creating_or_expanding),
            ms_until_next_spawn=self._passenger_spawner.ms_until_next_spawn,
            showing_debug=self.showing_debug,
            game_speed=self.game_speed,
        )

    def toggle_pause(self) -> None:
        if self.is_paused:
            self.steps_allowed = None
        if self.path_manager.editing_intermediate_stations:
            assert self.is_paused
            return
        self._components.status.is_paused = not self._components.status.is_paused

    def exit(self) -> NoReturn:
        pygame.quit()
        sys.exit()

    @property
    def travel_plans(self) -> TravelPlansMapping:
        return {
            passenger: passenger.travel_plan
            for passenger in self._components.passengers
            if passenger.travel_plan
        }

    @property
    def gui(self) -> GUI:
        return self._components.gui

    @property
    def is_paused(self) -> bool:
        return self._components.status.is_paused

    #######################
    ### private methods ###
    #######################

    def _move_metros(self, dt_ms: int) -> None:
        for path in self._components.paths:
            for metro in path.metros:
                path.move_metro(metro, dt_ms)

    def _move_passengers(self) -> None:
        for metro in self._components.metros:

            if not metro.current_station:
                continue

            self._passenger_mover.move_passengers(metro)
