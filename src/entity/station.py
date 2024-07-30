from __future__ import annotations

from typing import TYPE_CHECKING

from src.config import station_capacity, station_passengers_per_row, station_size
from src.geometry.point import Point
from src.geometry.shape import Shape
from src.geometry.utils import get_distance

from .holder import Holder
from .ids import create_new_station_id

if TYPE_CHECKING:
    from src.mediator import Mediator


class Station(Holder):
    __slots__ = ()

    def __init__(self, shape: Shape, position: Point, mediator: Mediator) -> None:
        super().__init__(
            shape=shape,
            capacity=station_capacity,
            id=create_new_station_id(shape.type),
            mediator=mediator,
        )
        self._size = station_size
        self.position = position
        self._passengers_per_row = station_passengers_per_row

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Station) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def get_distance_to(self, other: Station) -> float:
        return get_distance(self.position, other.position)
