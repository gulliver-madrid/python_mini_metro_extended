from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Iterator

from src.config import Config
from src.geometry.point import Point
from src.ui.ui import get_gui_height, get_main_surface_height
from src.utils import get_random_position, get_random_station_shape

from .metro import Metro
from .station import Station

if TYPE_CHECKING:
    from src.passengers_mediator import PassengersMediator


def get_random_station(passengers_mediator: PassengersMediator) -> Station:
    shape = get_random_station_shape()
    position = get_random_position(
        Config.screen_width, round(get_main_surface_height())
    )
    return Station(
        shape, position + Point(0, round(get_gui_height())), passengers_mediator
    )


def generate_stations(
    previous: Sequence[Station], passengers_mediator: PassengersMediator
) -> Iterator[Station]:
    while True:
        new_station = get_random_station(passengers_mediator)
        if all(
            station.get_distance_to(new_station) >= Config.min_distance
            for station in previous
        ):
            yield new_station


def get_random_stations(
    num: int, passengers_mediator: PassengersMediator
) -> list[Station]:
    stations: list[Station] = []
    generator = generate_stations(stations, passengers_mediator)
    for _ in range(num):
        stations.append(next(generator))
    return stations


def get_metros(num: int, passengers_mediator: PassengersMediator) -> list[Metro]:
    metros: list[Metro] = []
    for _ in range(num):
        metros.append(Metro(passengers_mediator))
    return metros
