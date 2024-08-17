from collections.abc import Sequence

import pygame

from src.config import Config
from src.engine.debug_renderer import DebugRenderer
from src.entity import Passenger, Path
from src.ui.ui import UI

from .game_components import GameComponents
from .passenger_spawner import TravelPlansMapping
from .path_edition import EditingIntermediateStations


class GameRenderer:
    __slots__ = ("_components", "debug_renderer")

    def __init__(self, components: GameComponents) -> None:
        self._components = components
        self.debug_renderer = DebugRenderer(self._components)

    def render_game(
        self,
        screen: pygame.surface.Surface,
        *,
        gui_height: float,
        main_surface_height: float,
        paths: Sequence[Path],
        editing_intermediate_stations: EditingIntermediateStations | None,
        max_num_paths: int,
        travel_plans: TravelPlansMapping,
        ui: UI,
        is_creating_path: bool,
        ms_until_next_spawn: float,
        showing_debug: bool,
        game_speed: float,
    ) -> None:
        main_surface = screen.subsurface(
            0, gui_height, Config.screen_width, main_surface_height
        )
        main_surface.fill((180, 180, 120))
        self._draw_paths(screen, paths)
        if editing_intermediate_stations:
            editing_intermediate_stations.draw(screen)
        for station in self._components.stations:
            station.draw(screen)
        for metro in self._components.metros:
            metro.draw(screen)
        ui.render(screen, self._components.status.score)
        passengers: Sequence[Passenger] = self._components.passengers
        if showing_debug:
            self.debug_renderer.draw_debug(
                screen,
                ui,
                is_creating_path,
                passengers,
                travel_plans,
                ms_until_next_spawn,
                game_speed,
            )

    def _draw_paths(
        self, screen: pygame.surface.Surface, paths: Sequence[Path]
    ) -> None:
        for path in paths:
            path.draw(screen)
