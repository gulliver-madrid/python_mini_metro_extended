from dataclasses import dataclass
from typing import Final

from src.config import Config, path_order_shift
from src.entity.ids import create_new_path_segment_id
from src.entity.station import Station
from src.geometry.line import Line
from src.geometry.point import Point
from src.geometry.types import create_degrees
from src.geometry.utils import get_direction
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
        edges = _get_segment_edges(self.stations, path_order)
        super().__init__(color, create_new_path_segment_id(), edges=edges)
        self._path_order = path_order
        self.line = Line(
            color=self.color,
            start=self.start,
            end=self.end,
            width=Config.path_width,
        )

    def repr(self) -> str:
        return f"{type(self).__name__}(id={self.num_id}, start={self.start}, end={self.end}, stations={self.stations})"


def _get_segment_edges(stations: StationPair, path_order: int) -> SegmentEdges:
    offset_vector = _get_offset_vector(stations, path_order)
    start = stations.start.position + offset_vector
    end = stations.end.position + offset_vector
    return SegmentEdges(start, end)


def _get_offset_vector(stations: StationPair, path_order: int) -> Point:
    start_point = stations.start.position
    end_point = stations.end.position
    direct = get_direction(start_point, end_point)
    buffer_vector = (direct * path_order_shift).rotate(create_degrees(90))
    return buffer_vector * path_order
