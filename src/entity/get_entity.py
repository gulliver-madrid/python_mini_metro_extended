from collections.abc import Sequence
from typing import Iterator, List

from src.config import screen_height, screen_width, station_size
from src.geometry.utils import distance
from src.utils import get_random_position, get_random_station_shape

from .metro import Metro
from .station import Station


def get_random_station() -> Station:
    shape = get_random_station_shape()
    position = get_random_position(screen_width, screen_height)
    return Station(shape, position)


def generate_stations(previous: Sequence[Station]) -> Iterator[Station]:
    min_distance = station_size * 2
    while True:
        new_station = get_random_station()
        if all(
            distance(station.position, new_station.position) >= min_distance
            for station in previous
        ):
            yield new_station


def get_random_stations(num: int) -> List[Station]:
    stations: List[Station] = []
    generator = generate_stations(stations)
    for _ in range(num):
        stations.append(next(generator))
    return stations


def get_metros(num: int) -> List[Metro]:
    metros: List[Metro] = []
    for _ in range(num):
        metros.append(Metro())
    return metros
