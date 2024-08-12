import math
from dataclasses import dataclass

from src.entity.path.state import PathState
from src.geometry.point import Point
from src.geometry.polygons import Polygon
from src.geometry.types import radians_to_degrees
from src.geometry.utils import get_direction, get_distance

from ..metro import Metro
from ..segments import PathSegment
from ..station import Station
from .end_segment_behaviour import (
    ChangeIndex,
    ReverseDirection,
    get_segment_behaviour_at_the_end_of_the_segment,
)


@dataclass
class MetroMovementSystem:
    """Delegated class of Path to manage metros movement"""

    _state: PathState

    ######################
    ### public methods ###
    ######################

    def move_metro(self, metro: Metro, dt_ms: int) -> None:
        dst_position, dst_station = _determine_destination(metro)

        distance_to_destination, direction = _calculate_direction_and_distance(
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

        behaviour = get_segment_behaviour_at_the_end_of_the_segment(
            len(self._state.segments),
            metro.current_segment_idx,
            metro.is_forward,
            self._state.is_looped,
        )
        while True:
            match behaviour:
                case ChangeIndex(value):
                    if value >= len(self._state.segments):
                        behaviour = ReverseDirection()
                        continue
                    metro.current_segment_idx = value
                    self._state.update_metro_current_segment(metro)
                case ReverseDirection():
                    metro.is_forward = not metro.is_forward
            break


#######################
### free functions ###
#######################


def _set_rotation_angle(polygon: Polygon, direct: Point) -> None:
    radians = math.atan2(direct.top, direct.left)
    degrees = radians_to_degrees(radians)
    polygon.set_degrees(degrees)


def _determine_destination(metro: Metro) -> tuple[Point, Station | None]:
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
    start_point: Point, end_point: Point
) -> tuple[float, Point]:
    """Calculate the distance and direction to the destination point"""
    distance = get_distance(start_point, end_point)
    direction = get_direction(start_point, end_point)
    return distance, direction
