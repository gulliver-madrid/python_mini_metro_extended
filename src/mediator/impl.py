from __future__ import annotations

from typing import TYPE_CHECKING, Final, Mapping

from src.config import Config
from src.entity.passenger import Passenger
from src.entity.station import Station
from src.protocols.travel_plan import TravelPlanProtocol

TravelPlans = dict[Passenger, TravelPlanProtocol]
TravelPlansMapping = Mapping[Passenger, TravelPlanProtocol]


class PassengerSpawning:
    if TYPE_CHECKING:
        __slots__ = (
            "_interval_step",
            "_ms_until_next_spawn",
        )

    def __init__(self, interval_step: int):
        self._interval_step: Final[int] = interval_step * 1000

        self._ms_until_next_spawn: float = (
            self._interval_step / Config.passenger_spawning.first_time_divisor
        )

    def is_passenger_spawn_time(self, status: MediatorStatus) -> bool:
        return self._ms_until_next_spawn <= 0

    def increment_time(self, dt_ms: int) -> None:
        self._ms_until_next_spawn -= dt_ms

    def reset(self) -> None:
        self._ms_until_next_spawn = self._interval_step

    @property
    def ms_until_next_spawn(self) -> float:
        return self._ms_until_next_spawn


def have_same_shape_type(station: Station, passenger: Passenger) -> bool:
    return station.shape.type == passenger.destination_shape.type


class MediatorStatus:
    if TYPE_CHECKING:
        __slots__ = (
            "is_creating_path",
            "is_paused",
            "score",
        )

    def __init__(self) -> None:
        self.is_creating_path: bool = False
        self.is_paused: bool = False
        self.score: int = 0
