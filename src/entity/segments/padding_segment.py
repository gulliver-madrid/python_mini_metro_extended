from dataclasses import dataclass
from typing import Final

from src.config import Config
from src.entity.ids import create_new_padding_segment_id
from src.entity.station import Station
from src.geometry.line import Line
from src.type import Color

from .segment import Segment, SegmentEdges


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
            path_order=path_order,
        )
        self.stations: Final = stations

    def set_edges(self, value: SegmentEdges) -> None:
        super().set_edges(value)
        self.line = Line(
            color=Config.padding_segments_color or self.color,
            start=self.start,
            end=self.end,
            width=Config.path_width,
        )

    def repr(self) -> str:
        return f"{type(self).__name__}(id={self.num_id}, start={self.start}, end={self.end}, stations={self.stations})"
