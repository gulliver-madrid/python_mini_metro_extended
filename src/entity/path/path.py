from collections.abc import Sequence
import itertools
from typing import Final

import pygame

from src.config import Config
from src.entity.path.metro_movement import MetroMovementSystem
from src.entity.path.state import PathState
from src.geometry.line import Line
from src.geometry.point import Point
from src.type import Color

from ..entity import Entity
from ..ids import create_new_path_id
from ..metro import Metro
from ..segments import PaddingSegment, PathSegment, Segment
from ..station import Station


class Path(Entity):
    __slots__ = (
        "color",
        "stations",
        "metros",
        "is_being_created",
        "selected",
        "temp_point",
        "_state",
        "_path_order",
        "temp_point_is_from_end",
        "_metro_movement_system",
    )

    def __init__(self, color: Color) -> None:
        super().__init__(create_new_path_id())

        # Final attributes
        self.color: Final = color
        self.stations: Final[list[Station]] = []
        self.metros: Final[list[Metro]] = []
        self._state: Final = PathState()
        self._metro_movement_system: Final = MetroMovementSystem(self._state)

        # Non-final attributes
        self.is_being_created = False
        self.selected = False
        self.temp_point: Point | None = None
        self.temp_point_is_from_end = True
        self._path_order = 0

    ########################
    ### public interface ###
    ########################

    @property
    def is_looped(self) -> bool:
        return self._state.is_looped

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
        segments: list[Segment] = _get_updated_segments(
            self.stations, self._state.is_looped, self.color, self._path_order
        )
        self._state.segments.clear()
        self._state.segments.extend(segments)

    def set_path_order(self, path_order: int) -> None:
        if path_order != self._path_order:
            self.update_segments()
            self._path_order = path_order

    def draw(self, surface: pygame.surface.Surface) -> None:
        if self.selected:
            self._draw_highlighted_stations(surface)

        for segment in self._state.segments:
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
        self._state.is_looped = True
        self.update_segments()

    def remove_loop(self) -> None:
        self._state.is_looped = False
        self.update_segments()

    def add_metro(self, metro: Metro) -> None:
        metro.shape.color = self.color
        self._state.update_metro_current_segment(metro)
        assert metro.current_segment
        metro.position = metro.current_segment.start
        metro.path_id = self.id
        # TODO: review this
        assert metro.current_segment.stations
        metro.current_station = metro.current_segment.stations.start
        self.metros.append(metro)

    def move_metro(self, metro: Metro, dt_ms: int) -> None:
        self._metro_movement_system.move_metro(metro, dt_ms)

    def get_containing_path_segment(self, position: Point) -> PathSegment | None:
        for segment in self.get_path_segments():
            if segment.includes(position):
                return segment
        return None

    def get_path_segments(self) -> list[PathSegment]:
        return [seg for seg in self._state.segments if isinstance(seg, PathSegment)]

    #########################
    ### private interface ###
    #########################

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


#######################
### free functions ###
#######################


def get_sign(s1: Station, s2: Station) -> int:
    assert s1.num_id != s2.num_id
    if s1.num_id > s2.num_id:
        return 1
    else:
        return -1


def _get_updated_segments(
    stations: Sequence[Station],
    is_looped: bool,
    color: Color,
    path_order: int,
) -> list[Segment]:

    path_segments: Sequence[PathSegment] = _create_path_segments(
        stations, color, path_order, is_looped
    )
    segments = _add_padding_segments(path_segments, color, is_looped)
    return segments


def _create_path_segments(
    stations: Sequence[Station],
    color: Color,
    path_order: int,
    is_looped: bool,
) -> list[PathSegment]:

    def create_path_segment(s1: Station, s2: Station) -> PathSegment:
        fixed_path_order = path_order * get_sign(s1, s2)
        return PathSegment(color, s1, s2, fixed_path_order)

    path_segments = [
        create_path_segment(s1, s2) for s1, s2 in itertools.pairwise(stations)
    ]
    if is_looped:
        closing_loop_segment = create_path_segment(stations[-1], stations[0])
        path_segments.append(closing_loop_segment)
    return path_segments


def _add_padding_segments(
    path_segments: Sequence[PathSegment],
    color: Color,
    is_looped: bool,
) -> list[Segment]:
    if not path_segments:
        return []
    segments: list[Segment] = []
    for current_segment, next_segment in itertools.pairwise(path_segments):
        segments.append(current_segment)
        segments.append(
            PaddingSegment(
                color,
                current_segment.end,
                next_segment.start,
            )
        )

    segments.append(path_segments[-1])

    if is_looped:
        segments.append(
            PaddingSegment(
                color,
                path_segments[-1].end,
                path_segments[0].start,
            )
        )
    return segments
