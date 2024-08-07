from dataclasses import dataclass, field

from src.engine.path_color_manager import PathColorManager
from src.entity import Metro, Passenger, Path, Station
from src.passengers_mediator import PassengersMediator
from src.ui.ui import UI

from .status import MediatorStatus


@dataclass(frozen=True)
class GameComponents:
    paths: list[Path]
    stations: list[Station]
    metros: list[Metro]
    status: MediatorStatus
    passengers_mediator: PassengersMediator
    path_color_manager: PathColorManager = field(
        init=False, default_factory=PathColorManager
    )
    ui: UI = field(init=False, default_factory=UI)

    @property
    def passengers(self) -> list[Passenger]:
        passengers: list[Passenger] = []
        for metro in self.metros:
            passengers.extend(metro.passengers)

        for station in self.stations:
            passengers.extend(station.passengers)
        return passengers
