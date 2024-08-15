from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Final, Iterable, TypeVar

import pygame

from src.entity.entity import Entity
from src.entity.ids import EntityId
from src.entity.segments.visual_segment import VisualSegment
from src.geometry.line import Line
from src.geometry.point import Point
from src.type import Color


@dataclass
class SegmentConnections:
    start: Segment | None = field(default=None)
    end: Segment | None = field(default=None)


class Segment(Entity, ABC):
    __slots__ = ("connections", "visual")

    def __init__(
        self,
        color: Color,
        id: EntityId,
    ) -> None:
        super().__init__(id)
        self.connections: Final = SegmentConnections()
        self.visual: Final = VisualSegment(color)

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.visual.draw(surface)

    def includes(self, position: Point) -> bool:
        return self.visual.includes(position)

    @property
    def start(self) -> Point:
        return self.visual.start

    @property
    def end(self) -> Point:
        return self.visual.end

    def repr(self) -> str:
        return f"{type(self).__name__}(id={self.num_id})"


T = TypeVar("T", bound=Segment)


def find_equal_segment(segment: T, segments: Iterable[T]) -> T | None:
    for s in segments:
        if segment == s:
            return s
    return None
