from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol

import pygame

from src.geometry.point import Point
from src.geometry.shape import Shape

from .entity import Entity
from .ids import create_new_passenger_id

if TYPE_CHECKING:
    from src.entity.path import Path
    from src.entity.station import Station
    from src.graph.node import Node


class TravelPlanProtocol(Protocol):
    next_path: Path | None
    next_station: Station | None
    node_path: Sequence[Node]

    def get_next_station(self) -> "Station | None": ...

    def increment_next_station(self) -> None: ...


class Passenger(Entity):
    __slots__ = (
        "position",
        "destination_shape",
        "is_at_destination",
        "travel_plan",
    )

    def __init__(self, destination_shape: Shape) -> None:
        super().__init__(create_new_passenger_id())
        self.position = Point(0, 0)
        self.destination_shape = destination_shape
        self.is_at_destination = False
        self.travel_plan: TravelPlanProtocol | None = None

    def __repr__(self) -> str:
        return f"{self.id}-{self.destination_shape.type}"

    def __str__(self) -> str:
        return repr(self) + f"-{self.destination_shape.type}"

    def __hash__(self) -> int:
        return hash(self.id)

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.destination_shape.draw(surface, self.position)
