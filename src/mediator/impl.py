from __future__ import annotations

from typing import Final

from src.entity.passenger import Passenger
from src.entity.path import Path
from src.entity.station import Station
from src.travel_plan import TravelPlan

TravelPlans = dict[Passenger, TravelPlan]


class PathBeingCreated:
    __slots__ = ("path",)

    def __init__(self, content: Path):
        self.path = content

    def add_station_to_path(self, station: Station) -> None:
        if self._is_last_station(station):
            return
        # loop
        if self.can_make_loop(station):
            self.path.set_loop()
        # non-loop
        elif not self._is_first_station(station):
            if self.path.is_looped:
                self.path.remove_loop()
            self.path.add_station(station)

    def can_end_with(self, station: Station) -> bool:
        stations = self.path.stations
        return len(stations) > 1 and self._is_last_station(station)

    def can_make_loop(self, station: Station) -> bool:
        stations = self.path.stations
        return len(stations) > 1 and self._is_first_station(station)

    def _is_first_station(self, station: Station) -> bool:
        return self.path.stations[0] == station

    def _is_last_station(self, station: Station) -> bool:
        return self.path.stations[-1] == station


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
