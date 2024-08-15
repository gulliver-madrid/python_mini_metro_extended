from dataclasses import dataclass
from typing import Final

from src.entity.ids import create_new_padding_segment_id
from src.entity.station import Station
from src.type import Color

from .segment import Segment


@dataclass(frozen=True)
class GroupOfThreeStations:
    previous: Station
    current: Station
    next: Station


class PaddingSegment(Segment):
    __slots__ = ("stations",)

    def __init__(self, color: Color, stations: GroupOfThreeStations) -> None:
        super().__init__(
            color,
            create_new_padding_segment_id(),
        )
        self.stations: Final = stations

    def __eq__(self, other: object) -> bool:
        return type(other) == PaddingSegment and other.stations == self.stations

    def __hash__(self) -> int:
        return hash(self.stations)

    def repr(self) -> str:
        return f"{type(self).__name__}(id={self.num_id}, previous={self.stations.previous}, current={self.stations.current}, next={self.stations.next})"
