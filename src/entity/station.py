from __future__ import annotations

from src.config import station_capacity, station_passengers_per_row, station_size
from src.geometry.point import Point
from src.geometry.shape import Shape
from src.geometry.utils import get_distance
from src.protocols.passenger_mediator import PassengersMediatorProtocol

from .holder import Holder
from .ids import create_new_station_id


class Station(Holder):
    __slots__ = ()
    _size = station_size

    def __init__(
        self,
        shape: Shape,
        position: Point,
        passengers_mediator: PassengersMediatorProtocol,
    ) -> None:
        super().__init__(
            shape=shape,
            capacity=station_capacity,
            id=create_new_station_id(shape.type),
            passengers_per_row=station_passengers_per_row,
            mediator=passengers_mediator,
        )
        self.position = position

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Station) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def get_distance_to(self, other: Station) -> float:
        return get_distance(self.position, other.position)
