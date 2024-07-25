from __future__ import annotations

from typing import Final, Mapping

from src.config import Config
from src.entity.passenger import Passenger
from src.geometry.type import ShapeType
from src.protocols.travel_plan import TravelPlanProtocol

from .game_components import GameComponents
from .passenger_creator import PassengerCreator

TravelPlansMapping = Mapping[Passenger, TravelPlanProtocol]


class PassengerSpawner:
    __slots__ = (
        "_components",
        "_interval_step",
        "_ms_until_next_spawn",
    )

    def __init__(self, components: GameComponents, interval_step: int):
        self._components = components
        self._interval_step: Final[int] = interval_step * 1000

        self._ms_until_next_spawn: float = (
            self._interval_step / Config.passenger_spawning.first_time_divisor
        )

    ######################
    ### public methods ###
    ######################

    def increment_time(self, dt_ms: int) -> None:
        self._ms_until_next_spawn -= dt_ms

    def manage_passengers_spawning(self) -> None:
        if self._is_passenger_spawn_time():
            self._spawn_passengers()
            self._reset()

    @property
    def ms_until_next_spawn(self) -> float:
        return self._ms_until_next_spawn

    #######################
    ### private methods ###
    #######################

    def _spawn_passengers(self) -> None:
        station_types = self._get_station_shape_types()
        passenger_creator = PassengerCreator(station_types)
        for station in self._components.stations:
            if not station.has_room():
                continue
            passenger = passenger_creator.create_passenger(station)
            station.add_passenger(passenger)

    def _get_station_shape_types(self) -> list[ShapeType]:
        station_shape_types: list[ShapeType] = []
        for station in self._components.stations:
            if station.shape.type not in station_shape_types:
                station_shape_types.append(station.shape.type)
        return station_shape_types

    def _is_passenger_spawn_time(self) -> bool:
        return self._ms_until_next_spawn <= 0

    def _reset(self) -> None:
        self._ms_until_next_spawn = self._interval_step
