from src.entity.passenger import Passenger
from src.config import station_capacity, station_passengers_per_row, station_size
from src.geometry.point import Point
from src.geometry.shape import Shape

from .holder import Holder
from .ids import create_new_station_id


class Station(Holder):
    __slots__ = ()

    def __init__(self, shape: Shape, position: Point) -> None:
        super().__init__(
            shape=shape,
            capacity=station_capacity,
            id=create_new_station_id(shape.type),
        )
        self.size = station_size
        self.position = position
        self.passengers_per_row = station_passengers_per_row

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Station) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def remove_passenger(self, passenger: Passenger) -> None:
        super().remove_passenger(passenger)
        # TODO: manage cases where station is removed before removing path
        passenger.last_station = self
