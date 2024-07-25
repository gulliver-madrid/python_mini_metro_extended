from src.config import path_order_shift, path_width
from src.geometry.line import Line
from src.geometry.utils import direction
from src.type import Color

from .ids import create_new_path_segment_id
from .segment import Segment, StationPair
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

        start_point = start_station.position
        end_point = end_station.position
        direct = direction(start_point, end_point)
        buffer_vector = direct * path_order_shift
        buffer_vector = buffer_vector.rotate(90)

        self.segment_start = start_station.position + buffer_vector * self._path_order
        self.segment_end = end_station.position + buffer_vector * self._path_order
        self.line = Line(
            color=self.color,
            start=self.segment_start,
            end=self.segment_end,
            width=path_width,
        )
