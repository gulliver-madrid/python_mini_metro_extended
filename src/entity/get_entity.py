from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Iterator

from src.config import Config, station_size
from src.geometry.point import Point
from src.geometry.utils import distance
from src.ui.ui import get_gui_height, get_main_surface_height
from src.utils import get_random_position, get_random_station_shape

from .metro import Metro
from .station import Station

if TYPE_CHECKING:
    from src.mediator import Mediator


def get_random_station() -> Station:
    shape = get_random_station_shape()
    position = get_random_position(
        Config.screen_width, round(get_main_surface_height())
    )
    return Station(shape, position + Point(0, round(get_gui_height())))


def generate_stations(previous: Sequence[Station]) -> Iterator[Station]:
    min_distance = station_size * 3
    while True:
        new_station = get_random_station()
        if all(
            distance(station.position, new_station.position) >= min_distance
            for station in previous
        ):
            yield new_station


def get_random_stations(num: int, mediator: Mediator | None = None) -> list[Station]:
    stations: list[Station] = []
    generator = generate_stations(stations)
    for _ in range(num):
        stations.append(next(generator))
        if mediator:
            stations[-1].mediator = mediator
    return stations


def get_metros(num: int) -> list[Metro]:
    metros: list[Metro] = []
    for _ in range(num):
        metros.append(Metro())
    return metros
