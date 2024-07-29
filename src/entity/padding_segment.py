from src.config import Config
from src.geometry.line import Line
from src.geometry.point import Point
from src.type import Color

from .ids import create_new_padding_segment_id
from .segment import PointPair, Segment


class PaddingSegment(Segment):
    __slots__ = ()

    def __init__(self, color: Color, start_point: Point, end_point: Point) -> None:
        super().__init__(color, create_new_padding_segment_id())
        self.points = PointPair(start_point, end_point)
        self.line = Line(
            color=Config.padding_segments_color or self.color,
            start=self.points.start,
            end=self.points.end,
            width=Config.path_width,
        )
