import pygame

from src.config import (
    button_color,
    button_size,
    path_button_buffer,
    path_button_cross_size,
    path_button_cross_width,
    path_button_dist_to_bottom,
    path_button_start_left,
)
from src.entity.path import Path
from src.geometry.circle import Circle
from src.geometry.point import Point
from src.geometry.polygons import Cross
from src.geometry.shape import Shape
from src.geometry.types import create_degrees
from src.gui.button import Button


class PathButton(Button):
    def __init__(self, shape: Shape, position: Point) -> None:
        super().__init__(shape)
        self.position = position
        self.path: Path | None = None
        self.cross: Cross | None = None
        self.show_cross = False

    def remove_path(self) -> None:
        self.cross = None
        self.path = None
        self.shape.color = button_color

    def assign_path(self, path: Path) -> None:
        self.cross = Cross((0, 0, 0), path_button_cross_size, path_button_cross_width)
        self.cross.set_degrees(create_degrees(45))
        self.path = path
        self.shape.color = path.color

    def on_hover(self) -> None:
        self.show_cross = True

    def on_exit(self) -> None:
        self.show_cross = False

    def on_click(self) -> None:
        self.remove_path()

    def draw(self, surface: pygame.surface.Surface) -> None:
        super().draw(surface)
        if self.cross and self.show_cross and self.path:
            self.cross.draw(surface, self.position)


def get_path_buttons(num: int) -> list[PathButton]:
    path_buttons: list[PathButton] = []
    for i in range(num):
        position = (
            Point(path_button_start_left, path_button_dist_to_bottom)
            + Point(i * path_button_buffer, 0)
            + Point(2 * i * button_size, 0)
        )
        path_buttons.append(PathButton(Circle(button_color, button_size), position))
    return path_buttons
