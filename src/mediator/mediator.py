from collections.abc import Sequence
import pprint
import sys
from typing import Final

import pygame

from src.config import (
    PassengerSpawningConfig,
    num_stations,
    screen_height,
    screen_width,
)
from src.entity.get_entity import get_random_stations
from src.entity.metro import Metro
from src.entity.passenger import Passenger
from src.entity.path import Path
from src.entity.station import Station
from src.geometry.point import Point
from src.geometry.type import ShapeType
from src.ui.path_button import PathButton
from src.ui.ui import UI, get_gui_height, get_main_surface_height

from .impl import MediatorStatus, PassengerCreator, PassengerSpawning, TravelPlans
from .passenger_mover import PassengerMover
from .path_manager import PathManager

pp = pprint.PrettyPrinter(indent=4)


class Mediator:
    __slots__ = (
        "_passenger_spawning",
        "num_stations",
        "stations",
        "metros",
        "passengers",
        "travel_plans",
        "_status",
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
            PassengerSpawningConfig.start_step, PassengerSpawningConfig.interval_step
        )
        self.num_stations: int = num_stations

        # entities
        self.stations: Final = get_random_stations(self.num_stations)
        self.metros: Final[list[Metro]] = []
        self.passengers: Final[list[Passenger]] = []

        # status
        self.travel_plans: Final[TravelPlans] = {}
        self._status: Final = MediatorStatus(PassengerSpawningConfig.interval_step)
        self.showing_debug = False
        self.game_speed = 1
        # UI
        self.ui = UI()
        self._game_renderer = GameRenderer()

        # delegated classes
        self.path_manager = PathManager(
            self.passengers,
            self.stations,
            self.travel_plans,
            self.metros,
            self._status,
            self.ui,
        )
        self._passenger_mover = PassengerMover(
            self.path_manager.paths, self.passengers, self.travel_plans, self._status
        )

        self.ui.init(self.path_manager.max_num_paths)

    ######################
    ### public methods ###
    ######################

    def set_clock(self, clock: pygame.time.Clock) -> None:
        self.ui.clock = clock

    def get_containing_entity(self, position: Point) -> Station | PathButton | None:
        for station in self.stations:
            if station.contains(position):
                return station
        return self.ui.get_containing_button(position) or None

    def increment_time(self, dt_ms: int) -> None:
        if self._status.is_paused:
            return

        dt_ms = dt_ms * self.game_speed
        self._status.increment_time(dt_ms, self.game_speed)

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
        self._game_renderer.render_game(
            screen,
            gui_height=self._gui_height,
            main_surface_height=self._main_surface_height,
            paths=self.paths,
            max_num_paths=self.path_manager.max_num_paths,
            stations=self.stations,
            metros=self.metros,
            score=self._status.score,
            ui=self.ui,
            showing_debug=self.showing_debug,
            game_speed=self.game_speed,
        )

    def toggle_pause(self) -> None:
        self._status.is_paused = not self._status.is_paused

    def exit(self) -> None:
        pygame.quit()
        sys.exit()

    @property
    def paths(self) -> list[Path]:
        return self.path_manager.paths

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

    def _get_station_shape_types(self) -> list[ShapeType]:
        station_shape_types: list[ShapeType] = []
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


class GameRenderer:
    def render_game(
        self,
        screen: pygame.surface.Surface,
        *,
        gui_height: float,
        main_surface_height: float,
        paths: Sequence[Path],
        max_num_paths: int,
        stations: Sequence[Station],
        metros: Sequence[Metro],
        score: int,
        ui: UI,
        showing_debug: bool,
        game_speed: float,
    ) -> None:
        main_surface = screen.subsurface(
            0, gui_height, screen_width, main_surface_height
        )
        main_surface.fill((180, 180, 120))
        self._draw_paths(screen, paths, max_num_paths)
        for station in stations:
            station.draw(screen)
        for metro in metros:
            metro.draw(screen)
        ui.render(screen, score)
        if showing_debug:
            fps = ui.clock.get_fps() if ui.clock else None
            self._draw_debug(screen, ui.small_font, ui.last_pos, fps, speed=game_speed)

    def _draw_paths(
        self, screen: pygame.surface.Surface, paths: Sequence[Path], max_num_paths: int
    ) -> None:
        for idx, path in enumerate(paths):
            path_order = idx - round(max_num_paths / 2)
            path.draw(screen, path_order)

    def _draw_debug(
        self,
        screen: pygame.surface.Surface,
        font: pygame.font.Font,
        mouse_pos: Point | None,
        fps: float | None,
        *,
        speed: float = 1.0,
    ) -> None:
        fg_color = (255, 255, 255)
        bg_color = (0, 0, 0)
        size = (300, 200)
        debug_surf = pygame.Surface(size)
        debug_surf.set_alpha(180)
        debug_surf.fill(bg_color)

        debug_texts: list[str] = []
        if mouse_pos:
            debug_texts.append(f"Mouse position: {mouse_pos.to_tuple()}")
        if fps:
            debug_texts.append(f"FPS: {fps:.2f}")
        debug_texts.append(f"Game speed: {speed:.2f}")

        self._draw_debug_texts(debug_surf, debug_texts, font, fg_color)

        screen.blit(debug_surf, (screen_width - size[0], screen_height - size[1]))

    def _draw_debug_texts(
        self,
        debug_surf: pygame.surface.Surface,
        debug_texts: list[str],
        font: pygame.font.Font,
        fg_color: tuple[int, int, int],
    ) -> None:
        for i, text in enumerate(debug_texts):
            debug_label = font.render(text, True, fg_color)
            debug_surf.blit(debug_label, (10, 10 + i * 30))
