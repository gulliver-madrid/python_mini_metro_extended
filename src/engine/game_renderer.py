from collections.abc import Sequence
from typing import Final

import pygame

from src.config import Config
from src.entity import Passenger, Path
from src.geometry.point import Point
from src.ui.ui import UI

from .game_components import GameComponents
from .passenger_spawner import TravelPlansMapping
from .path_edition import EditingIntermediateStations


class GameRenderer:
    __slots__ = ("_components", "debug_renderer")

    def __init__(self, components: GameComponents) -> None:
        self._components = components
        self.debug_renderer = DebugRenderer()

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
        self._draw_paths(screen, paths, max_num_paths)
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
        self, screen: pygame.surface.Surface, paths: Sequence[Path], max_num_paths: int
    ) -> None:
        for idx, path in enumerate(paths):
            path_order = idx - round(max_num_paths / 2)
            path.set_path_order(path_order)
            path.draw(screen)


class DebugRenderer:
    __slots__ = ("_debug_surf", "_position")

    fg_color: Final = (255, 255, 255)
    bg_color: Final = (0, 0, 0)
    size: Final = (300, 300)

    def __init__(self) -> None:
        self._debug_surf = pygame.Surface(self.size)
        self._position: Final = Point(
            Config.screen_width - self.size[0],
            Config.screen_height - self.size[1],
        )

    def draw_debug(
        self,
        screen: pygame.surface.Surface,
        ui: UI,
        is_creating_path: bool,
        passengers: Sequence[Passenger],
        travel_plans: TravelPlansMapping,
        ms_until_next_spawn: float,
        speed: float,
    ) -> None:
        font = ui.small_font
        mouse_pos = ui.last_pos
        fps = ui.clock.get_fps() if ui.clock else None
        self._debug_surf.set_alpha(180)
        self._debug_surf.fill(self.bg_color)

        debug_texts = self._define_debug_texts(
            mouse_pos,
            fps,
            passengers,
            travel_plans,
            ms_until_next_spawn=ms_until_next_spawn,
            is_creating_path=is_creating_path,
            game_speed=speed,
        )

        self._draw_debug_texts(debug_texts, font, self.fg_color)

        screen.blit(
            self._debug_surf,
            self._position.to_tuple(),
        )

    def _define_debug_texts(
        self,
        mouse_pos: Point | None,
        fps: float | None,
        passengers: Sequence[Passenger],
        travel_plans: TravelPlansMapping,
        *,
        ms_until_next_spawn: float,
        is_creating_path: bool,
        game_speed: float,
    ) -> list[str]:
        debug_texts: list[str] = []
        if mouse_pos:
            debug_texts.append(f"Mouse position: {mouse_pos.to_tuple()}")
        if fps:
            debug_texts.append(f"FPS: {fps:.2f}")
        debug_texts.append(f"Game speed: {game_speed:.2f}")
        debug_texts.append(f"Number of passengers: {len(passengers)}")
        debug_texts.append(f"Number of travel plans: {len(travel_plans)}")
        debug_texts.append(f"Until next spawning: { ( ms_until_next_spawn/1000):.2f}")
        debug_texts.append(f"Is creating path: { ( is_creating_path)}")
        return debug_texts

    def _draw_debug_texts(
        self,
        debug_texts: list[str],
        font: pygame.font.Font,
        fg_color: tuple[int, int, int],
    ) -> None:
        for i, text in enumerate(debug_texts):
            debug_label = font.render(text, True, fg_color)
            self._debug_surf.blit(debug_label, (10, 10 + i * 30))
