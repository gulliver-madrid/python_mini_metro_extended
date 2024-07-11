from typing import List

from src.config import screen_height, screen_width, station_size
from src.entity.metro import Metro
from src.entity.station import Station
from src.geometry.utils import distance
from src.utils import get_random_position, get_random_station_shape


def get_random_station() -> Station:
    shape = get_random_station_shape()
    position = get_random_position(screen_width, screen_height)
    return Station(shape, position)


def get_random_stations(num: int) -> List[Station]:
    min_distance = station_size * 2
    stations: List[Station] = []
    while len(stations) < num:
        new_station = get_random_station()
        if all(
            distance(station.position, new_station.position) >= min_distance
            for station in stations
        ):
            stations.append(new_station)
    return stations


def get_metros(num: int) -> List[Metro]:
    metros: List[Metro] = []
    for _ in range(num):
        metros.append(Metro())
    return metros
