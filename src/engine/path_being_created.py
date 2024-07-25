from __future__ import annotations

from typing import Final

from src.entity import Path, Station


class PathBeingCreated:
    __slots__ = ("path",)

    def __init__(self, path: Path):
        self.path: Final = path

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
        # non-loop
        else:
            assert not self._is_first_station(station)
            self.path.add_station(station)

    def can_end_with(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 1 and self._is_last_station(station)

    def can_make_loop(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 1 and self._is_first_station(station)

    #######################
    ### private methods ###
    #######################

    def _num_stations_in_this_path(self) -> int:
        return len(self.path.stations)

    def _is_first_station(self, station: Station) -> bool:
        return self.path.stations[0] == station

    def _is_last_station(self, station: Station) -> bool:
        return self.path.stations[-1] == station
