from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Final, Iterable, TypeVar

import pygame

from src.config import Config
from src.entity.entity import Entity
from src.entity.ids import EntityId
from src.entity.station import Station
from src.geometry.line import Line
from src.geometry.point import Point
from src.type import Color


@dataclass(frozen=True)
class StationPair:
    start: Station
    end: Station


@dataclass(frozen=True)
class SegmentEdges:
    start: Point
    end: Point


@dataclass
class SegmentConnections:
    start: Segment | None = field(default=None)
    end: Segment | None = field(default=None)


class Segment(Entity):
    __slots__ = ("color", "stations", "_edges", "line", "connections")

    line: Line

    def __init__(
        self,
        color: Color,
        id: EntityId,
        *,
        edges: SegmentEdges,
        stations: StationPair | None = None,
    ) -> None:
        super().__init__(id)
        self.color: Final = color
        self.stations: Final[StationPair | None] = stations
        self._edges: Final[SegmentEdges] = edges
        self.connections: Final = SegmentConnections()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Segment) and (self._edges == other._edges)

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.line.draw(surface)

    @property
    def start(self) -> Point:
        return self._edges.start

    @property
    def end(self) -> Point:
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


T = TypeVar("T", bound=Segment)


def find_equal_segment(segment: T, segments: Iterable[T]) -> T | None:
    for s in segments:
        if segment == s:
            return s
    return None
