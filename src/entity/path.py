import math
from itertools import pairwise
from typing import Final

import pygame

from src.config import Config
from src.entity.end_segment_behaviour import (
    ChangeIndex,
    ReverseDirection,
    get_segment_behaviour_at_the_end_of_the_segment,
)
from src.geometry.line import Line
from src.geometry.point import Point
from src.geometry.polygons import Polygon
from src.geometry.types import Degrees
from src.geometry.utils import get_direction, get_distance
from src.type import Color

from .entity import Entity
from .ids import create_new_path_id
from .metro import Metro
from .segments import PaddingSegment, PathSegment, Segment
from .station import Station


class Path(Entity):
    __slots__ = (
        "color",
        "stations",
        "metros",
        "is_looped",
        "is_being_created",
        "selected",
        "temp_point",
        "_segments",
        "_path_order",
        "temp_point_is_from_end",
    )
    _segments: Final[list[Segment]]

    def __init__(self, color: Color) -> None:
        super().__init__(create_new_path_id())
        self.color: Final = color
        self.stations: list[Station] = []
        self.metros: list[Metro] = []
        self.is_looped = False
        self.is_being_created = False
        self.selected = False
        self.temp_point: Point | None = None
        self.temp_point_is_from_end = True
        self._segments = []
        self._path_order = 0

    ########################
    ### public interface ###
    ########################

    @property
    def first_station(self) -> Station:
        return self.stations[0]

    @property
    def last_station(self) -> Station:
        return self.stations[-1]

    def add_station(self, station: Station) -> None:
        self.stations.append(station)
        self.update_segments()

    def update_segments(self) -> None:
        self._segments.clear()
        path_segments: list[Segment] = []

        # add path segments
        for i in range(len(self.stations) - 1):
            s1 = self.stations[i]
            s2 = self.stations[i + 1]
            path_segments.append(
                PathSegment(self.color, s1, s2, self._path_order * get_sign(s1, s2))
            )
            del s1, s2

        if self.is_looped:
            s1 = self.last_station
            s2 = self.first_station
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

    def set_path_order(self, path_order: int) -> None:
        if path_order != self._path_order:
            self.update_segments()
            self._path_order = path_order

    def draw_with_order(self, surface: pygame.surface.Surface, path_order: int) -> None:
        self._path_order = path_order
        self.draw(surface)

    def draw(self, surface: pygame.surface.Surface) -> None:
        if self.selected:
            self._draw_highlighted_stations(surface)

        for segment in self._segments:
            segment.draw(surface)

        if self.temp_point:
            start_line_station_index = -1 if self.temp_point_is_from_end else 0
            temp_line = Line(
                color=self.color,
                start=self.stations[start_line_station_index].position,
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
        distance_to_destination, direction = self._calculate_direction_and_distance(
            metro.position, dst_position
        )

        # Calculate and set the rotation angle of the metro
        if isinstance(metro.shape, Polygon):
            _set_rotation_angle(metro.shape, direction)

        # Calculate the distance the metro can travel in this time step
        distance_can_travel = metro.game_speed * dt_ms

        segment_end_reached = distance_can_travel >= distance_to_destination
        if segment_end_reached:
            self._handle_metro_movement_at_the_end_of_the_segment(metro, dst_station)
        else:
            metro.current_station = None
            metro.position += direction * distance_can_travel

    def get_containing_path_segment(self, position: Point) -> PathSegment | None:
        for segment in self.get_path_segments():
            if segment.includes(position):
                return segment
        return None

    def get_path_segments(self) -> list[PathSegment]:
        return [seg for seg in self._segments if isinstance(seg, PathSegment)]

    #########################
    ### private interface ###
    #########################

    def _determine_destination(self, metro: Metro) -> tuple[Point, Station | None]:
        """
        Determine the position and the possible station at the end of current segment.
        """
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
        distance = get_distance(start_point, end_point)
        direction = get_direction(start_point, end_point)
        return distance, direction

    def _handle_metro_movement_at_the_end_of_the_segment(
        self, metro: Metro, possible_dest_station: Station | None
    ) -> None:
        """Handle metro movement at the end of the segment"""
        # Update the current station if necessary
        if metro.current_station != possible_dest_station:
            metro.current_station = possible_dest_station

        behaviour = get_segment_behaviour_at_the_end_of_the_segment(
            len(self._segments),
            metro.current_segment_idx,
            metro.is_forward,
            self.is_looped,
        )
        while True:
            match behaviour:
                case ChangeIndex(value):
                    if value >= len(self._segments):
                        behaviour = ReverseDirection()
                        continue
                    metro.current_segment_idx = value
                    metro.current_segment = self._segments[metro.current_segment_idx]
                case ReverseDirection():
                    metro.is_forward = not metro.is_forward
            break

    def _draw_highlighted_stations(self, surface: pygame.surface.Surface) -> None:
        surface_size = surface.get_size()
        selected_surface = pygame.surface.Surface(surface_size, pygame.SRCALPHA)

        for station in self.stations:
            highlighted_shape = station.shape.get_scaled(1.2)
            highlighted_shape.color = self.color
            highlighted_shape.draw(
                selected_surface,
                station.position,
            )

        surface.blit(selected_surface, (0, 0))


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
