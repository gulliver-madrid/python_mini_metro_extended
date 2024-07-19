from __future__ import annotations

from typing import Final

from src.entity.passenger import Passenger
from src.entity.station import Station
from src.travel_plan import TravelPlan

TravelPlans = dict[Passenger, TravelPlan]


class PassengerSpawning:
    __slots__ = ("step", "interval_step")

    def __init__(self, start_step: int, interval_step: int):
        self.step: Final[int] = start_step
        self.interval_step: Final[int] = interval_step

    def is_passenger_spawn_time(self, status: MediatorStatus) -> bool:
        return (status.steps == self.step) or (
            status.steps_since_last_spawn >= self.interval_step
        )


def have_same_shape_type(station: Station, passenger: Passenger) -> bool:
    return station.shape.type == passenger.destination_shape.type


class MediatorStatus:
    __slots__ = (
        "_time_ms",
        "steps",
        "steps_since_last_spawn",
        "is_creating_path",
        "is_paused",
        "score",
    )

    def __init__(self, passenger_spawning_interval_step: int) -> None:
        self._time_ms: int = 0
        self.steps: float = 0
        self.steps_since_last_spawn: float = passenger_spawning_interval_step + 1
        self.is_creating_path: bool = False
        self.is_paused: bool = False
        self.score: int = 0

    def increment_time(self, dt_ms: int, game_speed: float) -> None:
        assert not self.is_paused

        self._time_ms += dt_ms
        self.steps += game_speed
        self.steps_since_last_spawn += game_speed
