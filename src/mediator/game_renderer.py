from collections.abc import Sequence

import pygame

from src.config import screen_height, screen_width
from src.entity.metro import Metro
from src.entity.path import Path
from src.entity.station import Station
from src.ui.ui import UI


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
            self._draw_debug(screen, ui, game_speed)

    def _draw_paths(
        self, screen: pygame.surface.Surface, paths: Sequence[Path], max_num_paths: int
    ) -> None:
        for idx, path in enumerate(paths):
            path_order = idx - round(max_num_paths / 2)
            path.draw(screen, path_order)

    def _draw_debug(self, screen: pygame.surface.Surface, ui: UI, speed: float) -> None:
        font = ui.small_font
        mouse_pos = ui.last_pos
        fps = ui.clock.get_fps() if ui.clock else None
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
