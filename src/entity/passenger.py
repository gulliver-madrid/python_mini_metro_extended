import pygame

from src.geometry.point import Point
from src.geometry.shape import Shape
from src.protocols.travel_plan import TravelPlanProtocol

from .entity import Entity
from .ids import create_new_passenger_id


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
