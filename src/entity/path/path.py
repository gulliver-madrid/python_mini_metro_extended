from __future__ import annotations

import itertools
from collections.abc import Sequence
from typing import Final

import pygame

from src.config import Config
from src.entity.path.metro_movement import MetroMovementSystem
from src.entity.path.state import PathState
from src.entity.segments.location import LocationService
from src.entity.segments.padding_segment import GroupOfThreeStations
from src.entity.travel_step import TravelStep
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
        "_location_service",
    )

    def __init__(self, color: Color, path_order: int) -> None:
        super().__init__(create_new_path_id())

        # Final attributes
        self.color: Final = color
        self.stations: Final[list[Station]] = []
        self.metros: Final[list[Metro]] = []
        self._state: Final = PathState()
        self._metro_movement_system: Final = MetroMovementSystem(self._state)
        self._location_service: Final = LocationService()

        # Non-final attributes
        self.is_being_created = False
        self.selected = False
        self.temp_point: Point | None = None
        self.temp_point_is_from_end = True
        self._path_order = path_order

    def __del__(self) -> None:
        if Config.debug_path_and_metros:
            print("Deleting path")

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
        """This should be called only when it is really needed"""
        segments: list[Segment] = _get_updated_segments(
            self.stations, self._state.is_looped, self.color
        )
        if segments:
            travel_step = build_travel_steps(segments, self.is_looped)
            assert travel_step.current == segments[0]
            assert travel_step.is_forward
            if self.metros:
                metro = self.metros[0]
                assert metro
                assert metro.travel_step
                assert metro.travel_step.next
                # trigger the clearing of references
                metro.travel_step.next = None
                metro.travel_step = travel_step
        self._state.segments.clear()
        self._state.segments.extend(segments)
        for segment in self._state.segments:
            self._location_service.locate_segment(segment, self._path_order)

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
        assert not metro.travel_step
        metro.shape.color = self.color
        metro.travel_step = build_travel_steps(self._state.segments, self.is_looped)
        assert metro.current_segment
        metro.position = metro.current_segment.start
        metro.path_id = self.id

        if isinstance(metro.current_segment, PathSegment):
            metro.current_station = metro.current_segment.stations.start
        else:
            assert isinstance(metro.current_segment, PaddingSegment)
            metro.current_station = metro.current_segment.stations.previous

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


def build_travel_steps(segments: Sequence[Segment], is_looped: bool) -> TravelStep:
    assert len(set(segments)) == len(segments)
    travel_step: TravelStep | None = None
    current_index = 0
    is_forward = True
    previous: TravelStep | None = None
    created: dict[tuple[int, bool], TravelStep] = {}
    building = True
    while building:
        travel_step = created.get((current_index, is_forward))
        if not travel_step:
            travel_step = TravelStep(segments[current_index], is_forward)
            created[(current_index, is_forward)] = travel_step
        else:
            building = False

        if previous:
            assert not previous.next
            previous.next = travel_step

        if not building:
            break

        if is_forward:
            if current_index < len(segments) - 1:
                current_index += 1
            elif is_looped:
                current_index = 0
            else:
                is_forward = False
        else:
            if current_index > 0:
                current_index -= 1
            elif is_looped:
                current_index = len(segments) - 1
            else:
                is_forward = True

        previous = travel_step
    assert travel_step
    return travel_step


def _get_updated_segments(
    stations: Sequence[Station],
    is_looped: bool,
    color: Color,
) -> list[Segment]:

    path_segments: Sequence[PathSegment] = _create_path_segments(
        stations, color, is_looped
    )
    segments = _add_padding_segments(path_segments, color, is_looped)
    _update_connections(segments)
    return segments


def _create_path_segments(
    stations: Sequence[Station],
    color: Color,
    is_looped: bool,
) -> list[PathSegment]:

    def create_path_segment(s1: Station, s2: Station) -> PathSegment:
        return PathSegment(color, s1, s2)

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
        assert current_segment.stations.end is next_segment.stations.start
        padding_segment = PaddingSegment(
            color,
            GroupOfThreeStations(
                current_segment.stations.start,
                current_segment.stations.end,
                next_segment.stations.end,
            ),
        )

        segments.append(padding_segment)

    segments.append(path_segments[-1])

    if is_looped:
        prev_segment = path_segments[-1]
        next_segment = path_segments[0]
        assert prev_segment.stations.end is next_segment.stations.start
        segments.append(
            PaddingSegment(
                color,
                GroupOfThreeStations(
                    prev_segment.stations.start,
                    prev_segment.stations.end,
                    next_segment.stations.end,
                ),
            )
        )
    return segments


def _update_connections(segments: Sequence[Segment]) -> None:
    for current, next_segment in itertools.pairwise(segments):
        current.connections.end = next_segment
        next_segment.connections.start = current
