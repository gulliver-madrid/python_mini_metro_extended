from __future__ import annotations

import random
from collections.abc import Sequence
from typing import Dict, Final, Mapping

from src.config import passenger_color, passenger_size
from src.entity.passenger import Passenger
from src.entity.path import Path
from src.entity.station import Station
from src.geometry.type import ShapeType
from src.travel_plan import TravelPlan
from src.utils import get_shape_from_type

TravelPlans = Dict[Passenger, TravelPlan]


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
            status.steps_since_last_spawn == self.interval_step
        )


def have_same_shape_type(station: Station, passenger: Passenger) -> bool:
    return station.shape.type == passenger.destination_shape.type


class PassengerCreator:
    shape_types_to_others: Final[Mapping[ShapeType, Sequence[ShapeType]]]

    def __init__(self, station_types: Sequence[ShapeType]):
        self.shape_types_to_others = {
            shape_type: [x for x in station_types if x != shape_type]
            for shape_type in set(station_types)
        }

    def create_passenger(self, station: Station) -> Passenger:
        other_shape_types = self.shape_types_to_others[station.shape.type]
        destination_shape_type = random.choice(other_shape_types)
        destination_shape = get_shape_from_type(
            destination_shape_type, passenger_color, passenger_size
        )
        return Passenger(destination_shape)


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
        self.steps: int = 0
        self.steps_since_last_spawn: int = passenger_spawning_interval_step + 1
        self.is_creating_path: bool = False
        self.is_paused: bool = False
        self.score: int = 0

    def increment_time(self, dt_ms: int) -> None:
        assert not self.is_paused

        self._time_ms += dt_ms
        self.steps += 1
        self.steps_since_last_spawn += 1
