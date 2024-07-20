from __future__ import annotations

from typing import TYPE_CHECKING, Final, Mapping

from src.entity.passenger import Passenger
from src.entity.station import Station
from src.protocols.travel_plan import TravelPlanProtocol

TravelPlans = dict[Passenger, TravelPlanProtocol]
TravelPlansMapping = Mapping[Passenger, TravelPlanProtocol]


class PassengerSpawning:
    if TYPE_CHECKING:
        __slots__ = ("step", "interval_step")

    def __init__(self, interval_step: int):
        self.interval_step: Final[int] = interval_step * 1000

    def is_passenger_spawn_time(self, status: MediatorStatus) -> bool:
        return status.ms_until_next_spawn <= 0


def have_same_shape_type(station: Station, passenger: Passenger) -> bool:
    return station.shape.type == passenger.destination_shape.type


class MediatorStatus:
    if TYPE_CHECKING:
        __slots__ = (
            "ms_until_next_spawn",
            "is_creating_path",
            "is_paused",
            "score",
        )

    def __init__(self, initial_ms_until_next_spawn: float) -> None:
        self.ms_until_next_spawn: float = initial_ms_until_next_spawn
        self.is_creating_path: bool = False
        self.is_paused: bool = False
        self.score: int = 0

    def increment_time(self, dt_ms: int) -> None:
        assert not self.is_paused

        self.ms_until_next_spawn -= dt_ms
