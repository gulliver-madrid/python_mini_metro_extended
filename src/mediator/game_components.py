from dataclasses import dataclass

from src.entity.metro import Metro
from src.entity.station import Station
from src.mediator.impl import MediatorStatus


@dataclass(frozen=True)
class GameComponents:
    stations: list[Station]
    metros: list[Metro]
    status: MediatorStatus
