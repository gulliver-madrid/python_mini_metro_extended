"""Location service that provides position to segments edges"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from src.config import path_order_shift
from src.entity.station import Station
from src.geometry.point import Point
from src.geometry.types import create_degrees
from src.geometry.utils import get_direction

from .segment import SegmentEdges

if TYPE_CHECKING:
    from src.entity.segments.padding_segment import GroupOfThreeStations
    from src.entity.segments.path_segment import StationPair

PathOrder = int


class LocationService:
    def __init__(self) -> None:
        # positions of PathSegment start from a point to another (the nearest to the first station of the tuple)
        self.connection_positions: Final[
            dict[tuple[Station, Station, PathOrder], Point]
        ] = {}

    def clear(self) -> None:
        self.connection_positions.clear()

    def get_padding_segment_edges(
        self, stations: GroupOfThreeStations, path_order: int
    ) -> SegmentEdges:
        from src.entity.segments.path_segment import StationPair

        prev_edges = self.get_path_segment_edges(
            StationPair(stations.previous, stations.current), path_order
        )
        next_edges = self.get_path_segment_edges(
            StationPair(stations.current, stations.next), path_order
        )
        return SegmentEdges(prev_edges.end, next_edges.start)

    def get_path_segment_edges(
        self, stations: StationPair, path_order: int
    ) -> SegmentEdges:
        offset_vector = _get_offset_vector(stations, path_order)
        start_key = (stations.start, stations.end, path_order)
        start = self.connection_positions.get(start_key)
        if not start:
            start = stations.start.position + offset_vector
            self.connection_positions[start_key] = start
        else:
            assert start == stations.start.position + offset_vector

        end_key = (stations.end, stations.start, path_order)
        end = self.connection_positions.get(end_key)
        if not end:
            end = stations.end.position + offset_vector
            self.connection_positions[end_key] = end
        else:
            assert end == stations.end.position + offset_vector
        return SegmentEdges(start, end)


def _get_offset_vector(stations: StationPair, path_order: int) -> Point:
    factor = _get_sign_using_station_num_id(stations.start, stations.end)
    start_point = stations.start.position
    end_point = stations.end.position

    direct = get_direction(start_point, end_point)
    buffer_vector = (direct * path_order_shift).rotate(create_degrees(90))
    return buffer_vector * (path_order) * factor


def _get_sign_using_station_num_id(s1: Station, s2: Station) -> int:
    assert s1.num_id != s2.num_id
    if s1.num_id > s2.num_id:
        return 1
    else:
        return -1
