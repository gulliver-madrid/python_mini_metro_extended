import math
from dataclasses import dataclass

import pygame

from src.geometry.line import Line
from src.geometry.point import Point
from src.type import Color

from .entity import Entity
from .ids import EntityId
from .station import Station


@dataclass
class StationPair:
    start: Station
    end: Station


@dataclass
class PointPair:
    start: Point
    end: Point

    def includes(self, position: Point) -> bool:
        dist = distance_point_segment(
            self.start.left,
            self.start.top,
            self.end.left,
            self.end.top,
            position.left,
            position.top,
        )
        return dist is not None and dist < 10


class Segment(Entity):
    __slots__ = (
        "color",
        "stations",
        "points",
        "line",
    )
    stations: StationPair | None
    points: PointPair
    line: Line

    def __init__(self, color: Color, id: EntityId) -> None:
        super().__init__(id)
        self.color = color
        self.stations = None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Segment) and self.id == other.id

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
