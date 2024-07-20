from typing import TYPE_CHECKING, Sequence

import pygame

from src.config import (
    Config,
    gui_height_proportion,
    score_display_coords,
    score_font_size,
)
from src.entity.path import Path
from src.geometry.point import Point
from src.ui.path_button import PathButton, get_path_buttons

_gui_height = Config.screen_height * gui_height_proportion
_main_surface_height = Config.screen_height - _gui_height


def get_gui_height() -> float:
    return _gui_height


def get_main_surface_height() -> float:
    return _main_surface_height


class UI:
    if TYPE_CHECKING:
        __slots__ = (
            "path_buttons",
            "path_to_button",
            "buttons",
            "font",
            "small_font",
            "last_pos",
            "clock",
        )

    def init(self, max_num_paths: int) -> None:
        pygame.font.init()
        self.path_to_button: dict[Path, PathButton] = {}

        self.font = pygame.font.SysFont("arial", score_font_size)
        self.small_font = pygame.font.SysFont("arial", 18)
        self.path_buttons: Sequence[PathButton] = get_path_buttons(max_num_paths)
        self.buttons = [*self.path_buttons]
        self.last_pos: Point | None = None
        self.clock: pygame.time.Clock | None = None

    def assign_paths_to_buttons(self, paths: Sequence[Path]) -> None:
        for path_button in self.path_buttons:
            path_button.remove_path()

        self.path_to_button = {}
        for i in range(min(len(paths), len(self.path_buttons))):
            path = paths[i]
            button = self.path_buttons[i]
            button.assign_path(path)
            self.path_to_button[path] = button

    def exit_buttons(self) -> None:
        for button in self.buttons:
            button.on_exit()

    def get_containing_button(self, position: Point) -> PathButton | None:
        for button in self.buttons:
            if button.contains(position):
                return button
        return None

    def render(self, screen: pygame.surface.Surface, score: int) -> None:
        gui_height = get_gui_height()
        gui = screen.subsurface(0, 0, screen.get_width(), gui_height)
        gui.fill((220, 220, 220))
        for button in self.buttons:
            button.draw(gui)
        text_surface = self.font.render(f"Score: {score}", True, (0, 0, 0))
        gui.blit(text_surface, score_display_coords)
