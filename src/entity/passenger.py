from typing import TYPE_CHECKING

import pygame

from src.geometry.point import Point
from src.geometry.shape import Shape
from src.protocols.travel_plan import TravelPlanProtocol

from .entity import Entity
from .ids import create_new_passenger_id

if TYPE_CHECKING:
    from .station import Station


class Passenger(Entity):
    __slots__ = (
        "position",
        "destination_shape",
        "is_at_destination",
        "_travel_plan",
        "last_station",
    )

    def __init__(self, destination_shape: Shape) -> None:
        super().__init__(create_new_passenger_id())
        self.position = Point(0, 0)
        self.destination_shape = destination_shape
        self.is_at_destination = False
        self._travel_plan: TravelPlanProtocol | None = None
        # last_station is used to reposition the passenger if their metro
        # is removed
        self.last_station: Station | None = None

    def __str__(self) -> str:
        return repr(self) + f"-{self.destination_shape.type}"

    def __hash__(self) -> int:
        return hash(self.id)

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.destination_shape.draw(surface, self.position)

    @property
    def travel_plan(self) -> TravelPlanProtocol | None:
        return self._travel_plan

    @travel_plan.setter
    def travel_plan(self, value: TravelPlanProtocol | None) -> None:
        if self._travel_plan and value:
            assert value.node_path != self._travel_plan.node_path
        self._travel_plan = value
