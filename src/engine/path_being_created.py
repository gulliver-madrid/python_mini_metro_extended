from __future__ import annotations

from typing import Final

from src.config import Config
from src.entity import Path, Station


class PathBeingCreatedOrExpanding:
    """Created or expanding"""

    __slots__ = (
        "path",
        "is_expanding",  # it can be edition or creation
        "_from_end",
    )

    def __init__(self, path: Path, station: Station | None = None):
        self.path: Final = path
        self.is_expanding: Final = station is not None
        self.set_from_end_value(station is None or not self._is_first_station(station))

    ######################
    ### public methods ###
    ######################

    def add_station_to_path(self, station: Station) -> bool:
        """Returns True if it should be inserted at start instead"""
        # TODO: improve this, avoid having to return a boolean
        if self.is_expanding and not self._from_end:
            if self._is_first_station(station):
                return False
            assert not self.path.is_looped
            # loop
            can_make_loop = (
                self._num_stations_in_this_path() > 2 and self._is_last_station(station)
            )
            if can_make_loop:
                if not self._from_end:
                    raise NotImplementedError
                self.path.set_loop()  # TODO: adapt to expanding from start
                return False
            # not allowing cross lines this way
            # TODO: make consistent (allowing or not crossing lines when creating or expanding)
            if station not in self.path.stations:
                return True
            return False

        assert self._from_end
        if self._is_last_station(station):
            return False
        assert not self.path.is_looped
        # loop
        if self.can_make_loop(station):
            self.path.set_loop()
            return False
        # non-loop
        allowed = Config.allow_self_crossing_lines or station not in self.path.stations
        if allowed:
            self.path.add_station(station)
        return False

    def can_end_with(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 1 and self._is_last_station(station)

    def can_make_loop(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 2 and self._is_first_station(station)

    def set_from_end_value(self, value: bool) -> None:
        self._from_end = value
        self.path.temp_point_is_from_end = value

    #######################
    ### private methods ###
    #######################

    def _num_stations_in_this_path(self) -> int:
        return len(self.path.stations)

    def _is_first_station(self, station: Station) -> bool:
        return self.path.stations[0] == station

    def _is_last_station(self, station: Station) -> bool:
        return self.path.stations[-1] == station
