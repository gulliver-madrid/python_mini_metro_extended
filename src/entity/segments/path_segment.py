from dataclasses import dataclass
from typing import Final

from src.config import Config
from src.entity.ids import create_new_path_segment_id
from src.entity.station import Station
from src.geometry.line import Line
from src.type import Color

from .segment import Segment, SegmentEdges


@dataclass(frozen=True)
class StationPair:
    start: Station
    end: Station


class PathSegment(Segment):
    __slots__ = ("_path_order", "stations")

    def __init__(
        self,
        color: Color,
        start_station: Station,
        end_station: Station,
        path_order: int,
    ) -> None:
        self.stations: Final = StationPair(start_station, end_station)

        super().__init__(color, create_new_path_segment_id(), path_order=path_order)
        self._path_order = path_order

    def set_edges(self, value: SegmentEdges) -> None:
        super().set_edges(value)
        self.line = Line(
            color=self.color,
            start=self.start,
            end=self.end,
            width=Config.path_width,
        )

    def repr(self) -> str:
        return f"{type(self).__name__}(id={self.num_id}, start={self.start}, end={self.end}, stations={self.stations})"
