from __future__ import annotations

from typing import Final

from src.config import Config
from src.entity import Path, Station


class PathBeingCreated:
    """Created or expanding"""

    __slots__ = (
        "path",
        "is_edition",
    )

    def __init__(self, path: Path, *, is_edition: bool = False):
        self.path: Final = path
        self.is_edition = is_edition

    ######################
    ### public methods ###
    ######################

    def add_station_to_path(self, station: Station) -> None:
        if self._is_last_station(station):
            return
        assert not self.path.is_looped
        # loop
        if self.can_make_loop(station):
            self.path.set_loop()
            return
        # non-loop
        allowed = Config.allow_self_crossing_lines or station not in self.path.stations
        if allowed:
            self.path.add_station(station)

    def can_end_with(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 1 and self._is_last_station(station)

    def can_make_loop(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 2 and self._is_first_station(station)

    #######################
    ### private methods ###
    #######################

    def _num_stations_in_this_path(self) -> int:
        return len(self.path.stations)

    def _is_first_station(self, station: Station) -> bool:
        return self.path.stations[0] == station

    def _is_last_station(self, station: Station) -> bool:
        return self.path.stations[-1] == station
