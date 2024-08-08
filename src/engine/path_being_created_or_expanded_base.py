from abc import ABC, abstractmethod
from typing import Final

from src.config import Config
from src.entity import Path, Station

from .game_components import GameComponents


class PathBeingCreatedOrExpandedBase(ABC):
    """Created or expanding"""

    __slots__ = (
        "path",
        "is_active",
        "_components",
        "is_expanding",
        "_from_end",
    )

    def __init__(
        self, components: GameComponents, path: Path, station: Station | None = None
    ):
        self.path: Final = path
        self.is_active = True
        self._components: Final = components
        self.is_expanding: Final = station is not None
        self._from_end: Final = station is None or self._is_last_station(station)
        self.path.temp_point_is_from_end = self._from_end

    def __bool__(self) -> bool:
        return self.is_active

    ######################
    ### public methods ###
    ######################

    @abstractmethod
    def add_station_to_path(self, station: Station) -> None:
        raise NotImplementedError

    @abstractmethod
    def try_to_end_path_on_station(self, station: Station) -> None:
        """
        The station should be in the path already, we are going to end path creation.
        """
        raise NotImplementedError

    def try_to_end_path_on_last_station(self) -> None:
        assert self.is_active
        last = self.path.stations[-1]
        self.try_to_end_path_on_station(last)

    @abstractmethod
    def abort_path_creation_or_expanding(self) -> None:
        raise NotImplementedError

    #######################
    ### private methods ###
    #######################

    @abstractmethod
    def _add_station_to_path(self, station: Station) -> bool:
        """Returns True if it should be inserted at start instead"""
        # TODO: improve this, avoid having to return a boolean
        raise NotImplementedError

    def _add_station_to_path_from_end(self, station: Station) -> None:
        assert self._from_end
        if self._is_last_station(station):
            return
        assert not self.path.is_looped
        # loop
        if self._can_make_loop(station):
            self.path.set_loop()
            return
        # non-loop
        allowed = Config.allow_self_crossing_lines or station not in self.path.stations
        if allowed:
            self.path.add_station(station)
        return

    def _stop_creating_or_expanding(self) -> None:
        assert self.is_active
        self.path.remove_temporary_point()
        self.path.selected = False
        self.is_active = False

    def _num_stations_in_this_path(self) -> int:
        return len(self.path.stations)

    def _is_first_station(self, station: Station) -> bool:
        return station is self.path.first_station

    def _is_last_station(self, station: Station) -> bool:
        return station is self.path.last_station

    def _can_make_loop(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 2 and self._is_first_station(station)
