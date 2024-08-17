from dataclasses import dataclass, field

from src.engine.path_color_manager import PathColorManager
from src.entity import Metro, Passenger, Path, Station
from src.gui.gui import GUI
from src.protocols.passenger_mediator import PassengersMediatorProtocol

from .status import EngineStatus


@dataclass(frozen=True)
class GameComponents:
    paths: list[Path]
    stations: list[Station]
    metros: list[Metro]
    status: EngineStatus
    passengers_mediator: PassengersMediatorProtocol
    path_color_manager: PathColorManager = field(
        init=False, default_factory=PathColorManager
    )
    gui: GUI = field(init=False, default_factory=GUI)

    @property
    def passengers(self) -> list[Passenger]:
        passengers: list[Passenger] = []
        for metro in self.metros:
            passengers.extend(metro.passengers)

        for station in self.stations:
            passengers.extend(station.passengers)
        return passengers
