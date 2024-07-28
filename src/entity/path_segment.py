from src.config import path_order_shift, path_width
from src.geometry.line import Line
from src.geometry.point import Point
from src.geometry.utils import get_direction
from src.type import Color

from .ids import create_new_path_segment_id
from .segment import PointPair, Segment, StationPair
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
        super().__init__(color, create_new_path_segment_id())
        self.stations = StationPair(start_station, end_station)
        self._path_order = path_order
        self.points = _get_segment_edges(self.stations, self._path_order)
        self.line = Line(
            color=self.color,
            start=self.points.start,
            end=self.points.end,
            width=path_width,
        )


def _get_segment_edges(stations: StationPair, path_order: int) -> PointPair:
    offset_vector = _get_offset_vector(stations, path_order)
    start = stations.start.position + offset_vector
    end = stations.end.position + offset_vector
    return PointPair(start, end)


def _get_offset_vector(stations: StationPair, path_order: int) -> Point:
    start_point = stations.start.position
    end_point = stations.end.position
    direct = get_direction(start_point, end_point)
    buffer_vector = (direct * path_order_shift).rotate(90)
    return buffer_vector * path_order
