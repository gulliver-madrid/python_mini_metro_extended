from __future__ import annotations

from typing import TYPE_CHECKING

from src.entity.path import Path
from src.entity.station import Station


class PathBeingCreated:
    if TYPE_CHECKING:
        __slots__ = ("path",)

    def __init__(self, path: Path):
        self.path = path

    # public methods

    def add_station_to_path(self, station: Station) -> None:
        if self._is_last_station(station):
            return
        # loop
        if self.can_make_loop(station):
            self.path.set_loop()
        # non-loop
        elif not self._is_first_station(station):
            if self.path.is_looped:
                self.path.remove_loop()
            self.path.add_station(station)

    def can_end_with(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 1 and self._is_last_station(station)

    def can_make_loop(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 1 and self._is_first_station(station)

    # private methods

    def _num_stations_in_this_path(self) -> int:
        return len(self.path.stations)

    def _is_first_station(self, station: Station) -> bool:
        return self.path.stations[0] == station

    def _is_last_station(self, station: Station) -> bool:
        return self.path.stations[-1] == station
