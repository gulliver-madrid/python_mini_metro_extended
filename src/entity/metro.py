from __future__ import annotations

from typing import Final

from src.config import (
    metro_capacity,
    metro_color,
    metro_passengers_per_row,
    metro_size,
    metro_speed_per_ms,
)
from src.entity.travel_step import TravelStep
from src.geometry.polygons import Rect
from src.protocols.passenger_mediator import PassengersMediatorProtocol

from .holder import Holder
from .ids import EntityId, create_new_metro_id
from .passenger import Passenger
from .segments import Segment
from .station import Station


class Metro(Holder):
    __slots__ = (
        "_current_station",
        "path_id",
        "travel_step",
    )
    game_speed: Final = metro_speed_per_ms
    _size = metro_size

    def __init__(self, passengers_mediator: PassengersMediatorProtocol) -> None:
        metro_shape = Rect(color=metro_color, width=2 * self._size, height=self._size)
        super().__init__(
            shape=metro_shape,
            capacity=metro_capacity,
            id=create_new_metro_id(),
            passengers_per_row=metro_passengers_per_row,
            mediator=passengers_mediator,
        )
        self._current_station: Station | None = None
        # self.current_segment: Segment | None = None
        # self.current_segment_idx = 0
        # self.is_forward = True
        self.travel_step: TravelStep | None = None
        self.path_id: EntityId | None = None

    ######################
    ### public methods ###
    ######################

    @property
    def current_segment(self) -> Segment:
        assert self.travel_step
        return self.travel_step.current

    @property
    def is_forward(self) -> bool:
        assert self.travel_step
        return self.travel_step.is_forward

    @property
    def current_station(self) -> Station | None:
        return self._current_station

    @current_station.setter
    def current_station(self, station: Station | None) -> None:
        self._current_station = station
        if station:
            self._update_passengers_last_station()

    def passenger_arrives(self, passenger: Passenger) -> None:
        assert passenger in self._passengers
        self._remove_passenger(passenger)

    #######################
    ### private methods ###
    #######################

    def _update_passengers_last_station(self) -> None:
        for passenger in self.passengers:
            passenger.last_station = self.current_station
