from dataclasses import dataclass
from typing import Final

from src.config import Config
from src.entity.ids import create_new_padding_segment_id
from src.entity.segments.location import LocationService
from src.entity.station import Station
from src.geometry.line import Line
from src.type import Color

from .segment import Segment


@dataclass(frozen=True)
class GroupOfThreeStations:
    previous: Station
    current: Station
    next: Station


class PaddingSegment(Segment):
    __slots__ = ("stations",)

    def __init__(
        self, color: Color, stations: GroupOfThreeStations, path_order: int
    ) -> None:
        super().__init__(
            color,
            create_new_padding_segment_id(),
            edges=LocationService.get_padding_segment_edges(stations, path_order),
        )
        self.stations: Final = stations
        self.line = Line(
            color=Config.padding_segments_color or self.color,
            start=self.start,
            end=self.end,
            width=Config.path_width,
        )

    def repr(self) -> str:
        return f"{type(self).__name__}(id={self.num_id}, start={self.start}, end={self.end}, stations={self.stations})"
