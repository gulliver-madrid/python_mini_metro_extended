from dataclasses import dataclass, field

import pygame

from src.color import reduce_saturation
from src.entity.path import Path
from src.entity.path_segment import PathSegment
from src.geometry.line import Line
from src.geometry.point import Point


@dataclass
class PathBeingEdited:
    path: Path
    segment: PathSegment
    temp_point: Point | None = field(default=None)

    def set_temporary_point(self, temp_point: Point) -> None:
        self.temp_point = temp_point

    def draw(self, surface: pygame.surface.Surface) -> None:
        color = reduce_saturation(self.path.color)
        if self.temp_point:
            temp_line1 = Line(
                color=color,
                start=self.segment.start,
                end=self.temp_point,
                width=10,
            )
            temp_line1.draw(surface)
            temp_line2 = Line(
                color=color,
                start=self.temp_point,
                end=self.segment.end,
                width=10,
            )
            temp_line2.draw(surface)
