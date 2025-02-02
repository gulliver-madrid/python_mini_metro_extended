import math
from dataclasses import dataclass

from src.entity.metro import Metro
from src.entity.segments import PaddingSegment, PathSegment
from src.entity.station import Station
from src.geometry.point import Point
from src.geometry.polygons import Polygon
from src.geometry.types import radians_to_degrees
from src.geometry.utils import get_direction, get_distance

from .state import PathState


@dataclass
class MetroMovementSystem:
    """Delegated class of Path to manage metros movement"""

    _state: PathState

    ######################
    ### public methods ###
    ######################

    def move_metro(self, metro: Metro, dt_ms: int) -> None:
        dst_position, dst_station = _determine_destination(metro)

        direction, distance_to_destination = _calculate_direction_and_distance(
            metro.position, dst_position
        )

        if isinstance(metro.shape, Polygon):
            _set_metro_rotation_angle(metro.shape, direction)

        distance_can_travel = metro.game_speed * dt_ms

        segment_end_reached = distance_can_travel >= distance_to_destination
        if segment_end_reached:
            self._handle_metro_movement_at_the_end_of_the_segment(metro, dst_station)
        else:
            metro.current_station = None
            metro.position += direction * distance_can_travel

    #######################
    ### private methods ###
    #######################

    def _handle_metro_movement_at_the_end_of_the_segment(
        self, metro: Metro, possible_dest_station: Station | None
    ) -> None:
        """Handle metro movement at the end of the segment"""
        # Update the current station if necessary
        if metro.current_station != possible_dest_station:
            metro.current_station = possible_dest_station
        assert metro.travel_step
        assert metro.travel_step.next
        metro.travel_step = metro.travel_step.next
        return


#########################
### private interface ###
#########################


def _set_metro_rotation_angle(polygon: Polygon, direct: Point) -> None:
    radians = math.atan2(direct.top, direct.left)
    degrees = radians_to_degrees(radians)
    polygon.set_degrees(degrees)


def _determine_destination(metro: Metro) -> tuple[Point, Station | None]:
    """
    Determine the position and the possible station at the end of current segment.
    """
    segment = metro.current_segment
    assert segment is not None

    dst_position = segment.end if metro.is_forward else segment.start

    if isinstance(segment, PathSegment):
        dst_station = (
            segment.stations.end if metro.is_forward else segment.stations.start
        )
    else:
        assert isinstance(segment, PaddingSegment)
        dst_station = None

    return dst_position, dst_station


def _calculate_direction_and_distance(
    start_point: Point, end_point: Point
) -> tuple[Point, float]:
    """Calculate the distance and direction to the destination point"""
    distance = get_distance(start_point, end_point)
    direction = get_direction(start_point, end_point)
    return direction, distance
