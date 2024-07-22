from dataclasses import dataclass

from src.entity import Metro, Path, Station
from src.mediator.status import MediatorStatus


@dataclass(frozen=True)
class GameComponents:
    paths: list[Path]
    stations: list[Station]
    metros: list[Metro]
    status: MediatorStatus
