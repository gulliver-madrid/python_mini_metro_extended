from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final, Sequence

import pygame

from src.config import passenger_display_buffer, passenger_size
from src.geometry.point import Point
from src.geometry.shape import Shape

from .entity import Entity
from .ids import EntityId
from .passenger import Passenger

if TYPE_CHECKING:
    from src.passengers_mediator import PassengersMediatorProtocol


class Holder(Entity):
    __slots__ = (
        "shape",
        "_capacity",
        "_passengers_per_row",
        "position",
        "_mediator",
        "_passengers",
    )

    _size: ClassVar[int] = 0
    position: Point

    def __init__(
        self,
        shape: Shape,
        capacity: int,
        id: EntityId,
        passengers_per_row: int,
        mediator: PassengersMediatorProtocol,
    ) -> None:
        super().__init__(id)
        assert self._size  # make sure derived class define it
        self.shape: Final[Shape] = shape
        self._capacity: Final[int] = capacity
        self._passengers_per_row: Final[int] = passengers_per_row
        self._mediator: Final[PassengersMediatorProtocol] = mediator
        self._mediator.register(self)
        self._passengers: Final[list[Passenger]] = []

    ######################
    ### public methods ###
    ######################

    def draw(self, surface: pygame.surface.Surface) -> None:
        self.shape.draw(surface, self.position)
        self._draw_passengers(surface)

    def contains(self, point: Point) -> bool:
        return self.shape.contains(point)

    def has_room(self) -> bool:
        return self.capacity > self.occupation

    def add_new_passenger(self, passenger: Passenger) -> None:
        self._mediator.on_new_passenger_added(passenger)
        self._add_passenger(passenger)

    def move_passenger(self, passenger: Passenger, dest: Holder) -> None:
        source = self
        self._mediator.on_passenger_exit(self, passenger)
        dest._add_passenger(passenger)
        source._remove_passenger(passenger)

    @property
    def passengers(self) -> Sequence[Passenger]:
        return self._passengers

    @property
    def occupation(self) -> int:
        return len(self._passengers)

    @property
    def capacity(self) -> int:
        return self._capacity

    #######################
    ### private methods ###
    #######################

    def _add_passenger(self, passenger: Passenger) -> None:
        assert self.has_room()
        self._passengers.append(passenger)

    def _remove_passenger(self, passenger: Passenger) -> None:
        assert passenger in self._passengers
        self._passengers.remove(passenger)

    def _draw_passengers(self, surface: pygame.surface.Surface) -> None:
        assert self._mediator
        abs_offset: Final = Point(
            (-passenger_size - passenger_display_buffer), 0.75 * self._size
        )
        base_position = self.position + abs_offset
        gap: Final = passenger_size / 2 + passenger_display_buffer
        row = 0
        col = 0
        for passenger in self.passengers:
            rel_offset = Point(col * gap, row * gap)
            passenger.position = base_position + rel_offset
            passenger.draw(surface)

            if col < (self._passengers_per_row - 1):
                col += 1
            else:
                row += 1
                col = 0
