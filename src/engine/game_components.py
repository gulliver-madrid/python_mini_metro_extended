from dataclasses import dataclass

from src.entity import Metro, Passenger, Path, Station
from src.passengers_mediator import PassengersMediator

from .status import MediatorStatus


@dataclass(frozen=True)
class GameComponents:
    paths: list[Path]
    stations: list[Station]
    metros: list[Metro]
    status: MediatorStatus
    passengers_mediator: PassengersMediator

    @property
    def passengers(self) -> list[Passenger]:
        passengers: list[Passenger] = []
        for metro in self.metros:
            passengers.extend(metro.passengers)

        for station in self.stations:
            passengers.extend(station.passengers)
        return passengers
