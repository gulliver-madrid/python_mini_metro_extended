from collections.abc import Sequence

from src.entity.path import Path
from src.entity.station import Station
from src.travel_plan import TravelPlan


def find_next_path_for_passenger_at_station(
    paths: Sequence[Path], travel_plan: TravelPlan, station: Station
) -> None:
    next_station = travel_plan.get_next_station()
    assert next_station is not None
    next_path = _find_shared_path(paths, station, next_station)
    travel_plan.next_path = next_path


def _find_shared_path(
    paths: Sequence[Path], station_a: Station, station_b: Station
) -> Path | None:
    """Returns the first path both stations belong to, or None if there is no shared path"""
    for path in paths:
        if all(station in path.stations for station in (station_a, station_b)):
            return path
    return None
