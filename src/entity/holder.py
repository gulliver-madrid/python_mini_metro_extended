from __future__ import annotations

from typing import TYPE_CHECKING, Final, Protocol, Sequence

import pygame

from src.config import passenger_display_buffer, passenger_size
from src.geometry.point import Point
from src.geometry.shape import Shape

from .entity import Entity
from .ids import EntityId
from .passenger import Passenger

if TYPE_CHECKING:
    from src.mediator import Mediator


class Holder(Entity):
    __slots__ = (
        "shape",
        "_capacity",
        "_passengers_per_row",
        "_size",
        "position",
        "mediator",
    )

    _passengers_per_row: int
    _size: int
    position: Point
    mediator: Final[Mediator]

    def __init__(
        self,
        shape: Shape,
        capacity: int,
        id: EntityId,
        mediator: Mediator,
    ) -> None:
        super().__init__(id)
        self.shape: Final = shape
        self._capacity: Final = capacity
        self.mediator = mediator

    ######################
    ### public methods ###
    ######################

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.shape.draw(surface, self.position)
        self._draw_passengers(surface)

    def contains(self, point: Point) -> bool:
        return self.shape.contains(point)

    def has_room(self) -> bool:
        assert self.mediator
        return self.mediator.holder_has_room(self)

    def add_new_passenger(self, passenger: Passenger) -> None:
        assert self.mediator
        self.mediator.add_new_passenger_to_holder(self, passenger)

    def move_passenger(self, passenger: Passenger, dest: Holder) -> None:
        assert self.mediator
        self.mediator.move_passenger(passenger, self, dest)

    @property
    def passengers(self) -> Sequence[Passenger]:
        assert self.mediator, self
        return self.mediator.get_passengers_in_holder(self)

    @property
    def occupation(self) -> int:
        assert self.mediator
        return self.mediator.get_holder_occupation(self)

    @property
    def capacity(self) -> int:
        return self._capacity

    #######################
    ### private methods ###
    #######################

    def _draw_passengers(self, surface: pygame.surface.Surface) -> None:
        assert self.mediator
        abs_offset: Final = Point(
            (-passenger_size - passenger_display_buffer), 0.75 * self._size
        )
        base_position = self.position + abs_offset
        gap: Final = passenger_size / 2 + passenger_display_buffer
        row = 0
        col = 0
        for passenger in self.mediator.get_passengers_in_holder(self):
            rel_offset = Point(col * gap, row * gap)
            passenger.position = base_position + rel_offset
            passenger.draw(surface)

            if col < (self._passengers_per_row - 1):
                col += 1
            else:
                row += 1
                col = 0


class HolderProtocol(Protocol):
    @property
    def capacity(self) -> int: ...
