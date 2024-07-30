from src.config import Config, path_order_shift
from src.geometry.line import Line
from src.geometry.point import Point
from src.geometry.types import Degrees
from src.geometry.utils import get_direction
from src.type import Color

from .ids import create_new_path_segment_id
from .segment import Segment, SegmentEdges, StationPair
from .station import Station


class PathSegment(Segment):
    __slots__ = ("_path_order",)

    def __init__(
        self,
        color: Color,
        start_station: Station,
        end_station: Station,
        path_order: int,
    ) -> None:
        stations = StationPair(start_station, end_station)
        edges = _get_segment_edges(stations, path_order)
        super().__init__(
            color, create_new_path_segment_id(), edges=edges, stations=stations
        )
        self._path_order = path_order
        self.line = Line(
            color=self.color,
            start=self.edges.start,
            end=self.edges.end,
            width=Config.path_width,
        )


def _get_segment_edges(stations: StationPair, path_order: int) -> SegmentEdges:
    offset_vector = _get_offset_vector(stations, path_order)
    start = stations.start.position + offset_vector
    end = stations.end.position + offset_vector
    return SegmentEdges(start, end)


def _get_offset_vector(stations: StationPair, path_order: int) -> Point:
    start_point = stations.start.position
    end_point = stations.end.position
    direct = get_direction(start_point, end_point)
    buffer_vector = (direct * path_order_shift).rotate(Degrees(90))
    return buffer_vector * path_order
