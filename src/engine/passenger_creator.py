from __future__ import annotations

import random
from collections.abc import Sequence
from typing import Final, Mapping

from src.config import passenger_color, passenger_size
from src.entity import Passenger, Station
from src.geometry.type import ShapeType
from src.utils import get_shape_from_type

ShapeTypesToOthers = Mapping[ShapeType, Sequence[ShapeType]]


class PassengerCreator:
    __slots__ = ("_shape_types_to_others",)
    _shape_types_to_others: Final[ShapeTypesToOthers]

    def __init__(self, station_types: Sequence[ShapeType]):
        self._shape_types_to_others = self._map_shape_types_to_others(station_types)

    # public methods

    def create_passenger(self, station: Station) -> Passenger:
        other_shape_types = self._shape_types_to_others[station.shape.type]
        destination_shape_type = random.choice(other_shape_types)
        return _create_passenger_with_shape_type(destination_shape_type)

    # private methods

    def _map_shape_types_to_others(
        self, station_types: Sequence[ShapeType]
    ) -> ShapeTypesToOthers:
        return {
            shape_type: [x for x in station_types if x != shape_type]
            for shape_type in set(station_types)
        }


def _create_passenger_with_shape_type(shape_type: ShapeType) -> Passenger:
    shape = get_shape_from_type(shape_type, passenger_color, passenger_size)
    return Passenger(shape)
