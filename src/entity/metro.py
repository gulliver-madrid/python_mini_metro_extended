from __future__ import annotations

from typing import TYPE_CHECKING

from src.config import (
    metro_capacity,
    metro_color,
    metro_passengers_per_row,
    metro_size,
    metro_speed_per_ms,
)
from src.geometry.rect import Rect

from .holder import Holder
from .ids import EntityId, create_new_metro_id
from .passenger import Passenger
from .segment import Segment
from .station import Station

if TYPE_CHECKING:
    from src.mediator import Mediator


class Metro(Holder):
    __slots__ = (
        "_current_station",
        "current_segment",
        "current_segment_idx",
        "path_id",
        "game_speed",
        "is_forward",
    )

    def __init__(self, mediator: Mediator) -> None:
        self._size = metro_size
        metro_shape = Rect(color=metro_color, width=2 * self._size, height=self._size)
        super().__init__(
            shape=metro_shape,
            capacity=metro_capacity,
            id=create_new_metro_id(),
            mediator=mediator,
        )
        self._current_station: Station | None = None
        self.current_segment: Segment | None = None
        self.current_segment_idx = 0
        self.path_id: EntityId | None = None
        self.game_speed = metro_speed_per_ms
        self.is_forward = True
        self._passengers_per_row = metro_passengers_per_row

    def passenger_arrives(self, passenger: Passenger) -> None:
        assert self.mediator
        self.mediator.passenger_arrives(self, passenger)

    @property
    def current_station(self) -> Station | None:
        return self._current_station

    @current_station.setter
    def current_station(self, value: Station | None) -> None:
        self._current_station = value
        if value is not None:
            self._update_passengers_last_station()

    def _update_passengers_last_station(self) -> None:
        for passenger in self.passengers:
            passenger.last_station = self.current_station
