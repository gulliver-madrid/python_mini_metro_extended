from collections.abc import Sequence
from typing import Final

import pygame

from src.config import Config
from src.entity.passenger import Passenger
from src.entity.path import Path
from src.geometry.point import Point
from src.mediator.game_components import GameComponents
from src.mediator.impl import TravelPlansMapping
from src.ui.ui import UI


class GameRenderer:
    def __init__(self) -> None:
        self.debug_renderer = DebugRenderer()

    def render_game(
        self,
        screen: pygame.surface.Surface,
        *,
        gui_height: float,
        main_surface_height: float,
        components: GameComponents,
        paths: Sequence[Path],
        max_num_paths: int,
        passengers: Sequence[Passenger],
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
        for station in components.stations:
            station.draw(screen)
        for metro in components.metros:
            metro.draw(screen)
        ui.render(screen, components.status.score)
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
            path.draw(screen, path_order)


class DebugRenderer:
    fg_color: Final = (255, 255, 255)
    bg_color: Final = (0, 0, 0)
    size: Final = (300, 200)

    def __init__(self) -> None:
        self._debug_surf = pygame.Surface(self.size)

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
            (Config.screen_width - self.size[0], Config.screen_height - self.size[1]),
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
