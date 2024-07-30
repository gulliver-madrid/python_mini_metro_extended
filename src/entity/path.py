import math
from itertools import pairwise
from typing import Final

import pygame

from src.config import Config
from src.entity.end_segment_behaviour import (
    ChangeIndex,
    ReverseDirection,
    get_segment_end_behaviour,
)
from src.geometry.line import Line
from src.geometry.point import Point
from src.geometry.polygon import Polygon
from src.geometry.types import Degrees
from src.geometry.utils import get_direction, get_distance
from src.type import Color

from .entity import Entity
from .ids import create_new_path_id
from .metro import Metro
from .padding_segment import PaddingSegment
from .path_segment import PathSegment
from .segment import Segment
from .station import Station


class Path(Entity):
    __slots__ = (
        "color",
        "stations",
        "metros",
        "is_looped",
        "is_being_created",
        "temp_point",
        "_segments",
        "_path_order",
    )
    _segments: Final[list[Segment]]

    def __init__(self, color: Color) -> None:
        super().__init__(create_new_path_id())
        self.color = color
        self.stations: list[Station] = []
        self.metros: list[Metro] = []
        self.is_looped = False
        self.is_being_created = False
        self.temp_point: Point | None = None
        self._segments = []
        self._path_order = 0

    def add_station(self, station: Station) -> None:
        self.stations.append(station)
        self.update_segments()

    def update_segments(self) -> None:
        self._segments.clear()
        path_segments: list[Segment] = []

        # add path segments
        s1 = s2 = None
        for i in range(len(self.stations) - 1):
            s1 = self.stations[i]
            s2 = self.stations[i + 1]
            path_segments.append(
                PathSegment(self.color, s1, s2, self._path_order * get_sign(s1, s2))
            )
        del s1, s2

        s1 = s2 = None
        if self.is_looped:
            s1 = self.stations[-1]
            s2 = self.stations[0]
            path_segments.append(
                PathSegment(self.color, s1, s2, self._path_order * get_sign(s1, s2))
            )
        del s1, s2

        # add padding segments
        for current_segment, next_segment in pairwise(path_segments):
            padding_segment = PaddingSegment(
                self.color,
                current_segment.end,
                next_segment.start,
            )
            self._segments.append(current_segment)
            self._segments.append(padding_segment)

        if path_segments:
            self._segments.append(path_segments[-1])

        if self.is_looped:
            padding_segment = PaddingSegment(
                self.color,
                path_segments[-1].end,
                path_segments[0].start,
            )
            self._segments.append(padding_segment)

    def draw(self, surface: pygame.surface.Surface, path_order: int) -> None:

        self._path_order = path_order
        self.update_segments()

        for segment in self._segments:
            segment.draw(surface)

        if self.temp_point:
            temp_line = Line(
                color=self.color,
                start=self.stations[-1].position,
                end=self.temp_point,
                width=Config.path_width,
            )
            temp_line.draw(surface)

    def set_temporary_point(self, temp_point: Point) -> None:
        self.temp_point = temp_point

    def remove_temporary_point(self) -> None:
        self.temp_point = None

    def set_loop(self) -> None:
        self.is_looped = True
        self.update_segments()

    def remove_loop(self) -> None:
        self.is_looped = False
        self.update_segments()

    def add_metro(self, metro: Metro) -> None:
        metro.shape.color = self.color
        metro.current_segment = self._segments[metro.current_segment_idx]
        metro.position = metro.current_segment.start
        metro.path_id = self.id
        # TODO: review this
        assert metro.current_segment.stations
        metro.current_station = metro.current_segment.stations.start
        self.metros.append(metro)

    def move_metro(self, metro: Metro, dt_ms: int) -> None:
        dst_position, dst_station = self._determine_destination(metro)

        # Calculate the distance and direction to the destination point
        dist, direction = self._calculate_direction_and_distance(
            metro.position, dst_position
        )

        # Calculate and set the rotation angle of the metro
        if isinstance(metro.shape, Polygon):
            _set_rotation_angle(metro.shape, direction)

        # Calculate the distance the metro can travel in this time step
        travel_dist_in_dt = metro.game_speed * dt_ms

        # If the metro has not reached the end of the segment
        if travel_dist_in_dt < dist:
            metro.current_station = None
            metro.position += direction * travel_dist_in_dt
        # If the metro has reached the end of the segment
        else:
            self._handle_segment_end(metro, dst_station)

    def get_containing_path_segment(self, position: Point) -> PathSegment | None:
        for segment in self.get_path_segments():
            if segment.includes(position):
                return segment
        return None

    def get_path_segments(self) -> list[PathSegment]:
        return [seg for seg in self._segments if isinstance(seg, PathSegment)]

    def _determine_destination(self, metro: Metro) -> tuple[Point, Station | None]:
        segment = metro.current_segment
        assert segment is not None

        if metro.is_forward:
            dst_position = segment.end
        else:
            dst_position = segment.start

        if isinstance(segment, PathSegment):
            assert segment.stations
            stations = segment.stations
            dst_station = stations.end if metro.is_forward else stations.start
        else:
            dst_station = None

        return dst_position, dst_station

    def _calculate_direction_and_distance(
        self, start_point: Point, end_point: Point
    ) -> tuple[float, Point]:
        dist = get_distance(start_point, end_point)
        direction = get_direction(start_point, end_point)
        return dist, direction

    def _handle_segment_end(self, metro: Metro, dst_station: Station | None) -> None:
        """Handle metro movement at the end of the segment"""
        # Update the current station if necessary
        if metro.current_station != dst_station:
            metro.current_station = dst_station

        behaviour = get_segment_end_behaviour(
            len(self._segments),
            metro.current_segment_idx,
            metro.is_forward,
            self.is_looped,
        )
        match behaviour:
            case ChangeIndex(value):
                metro.current_segment_idx = value
                metro.current_segment = self._segments[metro.current_segment_idx]
            case ReverseDirection():
                metro.is_forward = not metro.is_forward


def _set_rotation_angle(polygon: Polygon, direct: Point) -> None:
    radians = math.atan2(direct.top, direct.left)
    degrees = Degrees(math.degrees(radians))
    polygon.set_degrees((degrees))


def get_sign(s1: Station, s2: Station) -> int:
    assert s1.num_id != s2.num_id
    if s1.num_id > s2.num_id:
        return 1
    else:
        return -1
