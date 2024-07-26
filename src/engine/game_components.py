from dataclasses import dataclass

from src.entity import Metro, Passenger, Path, Station
from src.mediator import Mediator

from .status import MediatorStatus


@dataclass(frozen=True)
class GameComponents:
    paths: list[Path]
    stations: list[Station]
    metros: list[Metro]
    status: MediatorStatus
    mediator: Mediator

    @property
    def passengers(self) -> list[Passenger]:
        passengers: list[Passenger] = []
        for metro in self.metros:
            passengers.extend(metro.passengers)

        for station in self.stations:
            passengers.extend(station.passengers)
        return passengers
