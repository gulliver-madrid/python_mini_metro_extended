from itertools import pairwise
import math

from typing import Final

import pygame

from src.config import path_width
from src.geometry.line import Line
from src.geometry.point import Point
from src.geometry.utils import direction, distance
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
                current_segment.segment_end,
                next_segment.segment_start,
            )
            self._segments.append(current_segment)
            self._segments.append(padding_segment)

        if path_segments:
            self._segments.append(path_segments[-1])

        if self.is_looped:
            padding_segment = PaddingSegment(
                self.color,
                path_segments[-1].segment_end,
                path_segments[0].segment_start,
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
                width=path_width,
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
        metro.position = metro.current_segment.segment_start
        metro.path_id = self.id
        # TODO: review this
        assert metro.current_segment.stations
        metro.current_station = metro.current_segment.stations.start
        self.metros.append(metro)

    def move_metro(self, metro: Metro, dt_ms: int) -> None:
        segment = metro.current_segment
        assert metro.current_segment is not None

        if metro.is_forward:
            dst_position = metro.current_segment.segment_end
        else:
            dst_position = metro.current_segment.segment_start

        if isinstance(metro.current_segment, PathSegment):
            assert metro.current_segment.stations
            if metro.is_forward:
                dst_station = metro.current_segment.stations.end
            else:
                dst_station = metro.current_segment.stations.start
        else:
            dst_station = None

        start_point = metro.position
        end_point = dst_position
        dist = distance(start_point, end_point)
        direct = direction(start_point, end_point)
        radians = math.atan2(direct.top, direct.left)
        degrees = math.degrees(radians)
        metro.shape.set_degrees(degrees)
        travel_dist_in_dt = metro.game_speed * dt_ms
        # metro is not at one end of segment
        if dist > travel_dist_in_dt:
            metro.current_station = None
            metro.position += direct * travel_dist_in_dt
        # metro is at one end of segment
        else:
            if metro.current_station != dst_station:
                metro.current_station = dst_station
                for passenger in metro.passengers:
                    passenger.last_station = dst_station
            if len(self._segments) == 1:
                metro.is_forward = not metro.is_forward
            elif metro.current_segment_idx == len(self._segments) - 1:
                if self.is_looped:
                    metro.current_segment_idx = 0
                else:
                    if metro.is_forward:
                        metro.is_forward = False
                    else:
                        metro.current_segment_idx -= 1
            elif metro.current_segment_idx == 0:
                if metro.is_forward:
                    metro.current_segment_idx += 1
                else:
                    if self.is_looped:
                        metro.current_segment_idx = len(self._segments) - 1
                    else:
                        metro.is_forward = True
            else:
                if metro.is_forward:
                    metro.current_segment_idx += 1
                else:
                    metro.current_segment_idx -= 1

            metro.current_segment = self._segments[metro.current_segment_idx]


def get_sign(s1: Station, s2: Station) -> int:
    assert s1.num_id != s2.num_id
    if s1.num_id > s2.num_id:
        return 1
    else:
        return -1
