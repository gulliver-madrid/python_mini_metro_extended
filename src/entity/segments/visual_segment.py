from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

import pygame

from src.config import Config
from src.geometry.line import Line
from src.geometry.point import Point
from src.type import Color


@dataclass(frozen=True)
class SegmentEdges:
    start: Point
    end: Point


class VisualSegment:
    __slots__ = ("color", "_edges", "line")
    line: Line

    def __init__(
        self,
        color: Color,
    ) -> None:
        self.color: Final = color
        self._edges: SegmentEdges | None = None

    def set_edges(self, value: SegmentEdges) -> None:
        assert not self._edges
        self._edges = value
        self.line = Line(
            color=self.color,
            start=self.start,
            end=self.end,
            width=Config.path_width,
        )

    @property
    def start(self) -> Point:
        assert self._edges
        return self._edges.start

    @property
    def end(self) -> Point:
        assert self._edges
        return self._edges.end

    def includes(self, position: Point) -> bool:
        dist = distance_point_segment(
            self.start.left,
            self.start.top,
            self.end.left,
            self.end.top,
            position.left,
            position.top,
        )
        return dist is not None and dist < Config.path_width

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.line.draw(surface)


def distance_point_segment(
    Ax: float, Ay: float, Bx: float, By: float, Cx: float, Cy: float
) -> float | None:
    # Vector AB
    ABx = Bx - Ax
    ABy = By - Ay

    # Vector AC
    ACx = Cx - Ax
    ACy = Cy - Ay

    # Length of AB squared
    AB_length_sq = ABx**2 + ABy**2

    # Scalar projection of AC onto AB
    proj = (ACx * ABx + ACy * ABy) / AB_length_sq

    if proj <= 0:
        # C is closer to A
        return None
    elif proj >= 1:
        # C is closer to B
        return None
    else:
        # The projection falls within the segment
        proj_x = Ax + proj * ABx
        proj_y = Ay + proj * ABy
        return math.sqrt((Cx - proj_x) ** 2 + (Cy - proj_y) ** 2)
