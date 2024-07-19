from __future__ import annotations

import pygame

from src.config import passenger_display_buffer, passenger_size
from src.geometry.point import Point
from src.geometry.shape import Shape

from .entity import Entity
from .ids import EntityId
from .passenger import Passenger


class Holder(Entity):
    passengers_per_row: int
    size: int
    position: Point

    def __init__(self, shape: Shape, capacity: int, id: EntityId) -> None:
        super().__init__(id)
        self.shape = shape
        self.capacity = capacity
        self.passengers: list[Passenger] = []

    def draw(self, surface: pygame.surface.Surface) -> None:
        # draw self
        self.shape.draw(surface, self.position)

        # draw passengers
        row = 0
        col = 0
        for passenger in self.passengers:
            passenger.position = (
                self.position
                + Point((-passenger_size - passenger_display_buffer), 0.75 * self.size)
                + Point(
                    col * (passenger_size / 2 + passenger_display_buffer),
                    row * (passenger_size / 2 + passenger_display_buffer),
                )
            )

            passenger.draw(surface)

            if col < (self.passengers_per_row - 1):
                col += 1
            else:
                row += 1
                col = 0

    def contains(self, point: Point) -> bool:
        return self.shape.contains(point)

    def has_room(self) -> bool:
        return self.capacity > len(self.passengers)

    def add_passenger(self, passenger: Passenger) -> None:
        assert self.has_room()
        self.passengers.append(passenger)

    def remove_passenger(self, passenger: Passenger) -> None:
        assert passenger in self.passengers
        self.passengers.remove(passenger)

    def move_passenger(self, passenger: Passenger, holder: Holder) -> None:
        assert holder.has_room()
        holder.add_passenger(passenger)
        self.remove_passenger(passenger)
