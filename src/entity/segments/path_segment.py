from dataclasses import dataclass
from typing import Final

from src.entity.ids import create_new_path_segment_id
from src.entity.station import Station
from src.type import Color

from .segment import Segment


@dataclass(frozen=True)
class StationPair:
    start: Station
    end: Station


class PathSegment(Segment):
    __slots__ = ("stations",)

    def __init__(
        self,
        color: Color,
        start_station: Station,
        end_station: Station,
    ) -> None:
        self.stations: Final = StationPair(start_station, end_station)

        super().__init__(color, create_new_path_segment_id())

    def __eq__(self, other: object) -> bool:
        return type(other) == PathSegment and other.stations == self.stations

    def __hash__(self) -> int:
        return hash(self.stations)

    def repr(self) -> str:
        return f"{type(self).__name__}(id={self.num_id}, start={self.stations.start}, end={self.stations.end})"
