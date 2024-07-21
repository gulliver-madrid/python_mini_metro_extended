from dataclasses import dataclass

from src.entity.metro import Metro
from src.entity.station import Station


@dataclass(frozen=True)
class GameComponents:
    stations: list[Station]
    metros: list[Metro]
