from __future__ import annotations

from typing import Dict, Sequence

import pygame

from src.config import score_display_coords, score_font_size
from src.entity.path import Path
from src.geometry.point import Point
from src.ui.path_button import PathButton, get_path_buttons


class UI:
    __slots__ = (
        "path_buttons",
        "path_to_button",
        "buttons",
        "font",
    )

    def __init__(self, num_paths: int) -> None:
        pygame.font.init()

        # UI
        self.path_buttons: Sequence[PathButton] = get_path_buttons(num_paths)
        self.path_to_button: Dict[Path, PathButton] = {}
        self.buttons = [*self.path_buttons]
        self.font = pygame.font.SysFont("arial", score_font_size)

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
        for button in self.buttons:
            button.draw(screen)
        text_surface = self.font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(text_surface, score_display_coords)
