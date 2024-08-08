from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final

from src.config import Config, max_num_metros
from src.engine.utils import update_metros_segment_idx
from src.entity import Path, Station
from src.entity.metro import Metro

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

    def _insert_station(self, station: Station, index: int) -> None:
        assert self.is_active
        assert self.is_expanding
        path = self.path
        index = index - 1
        # we insert the station *after* that index
        path.stations.insert(index + 1, station)
        update_metros_segment_idx(path.metros, after_index=index, change=1)

    @abstractmethod
    def _add_station_to_path(self, station: Station) -> bool:
        """Returns True if it should be inserted at start instead"""
        # TODO: improve this, avoid having to return a boolean
        raise NotImplementedError

    def _add_station_to_path_from_end(self, station: Station) -> bool:
        """
        Returns True if it should be inserted at start instead
        """
        # TODO: improve this, avoid having to return a boolean
        assert self._from_end
        if self._is_last_station(station):
            return False
        assert not self.path.is_looped
        # loop
        if self._can_make_loop(station):
            self.path.set_loop()
            return False
        # non-loop
        allowed = Config.allow_self_crossing_lines or station not in self.path.stations
        if allowed:
            self.path.add_station(station)
        return False

    def _finish_path_creation(self) -> None:
        assert self.is_active
        self.path.is_being_created = False
        if self._can_add_metro():
            self._add_new_metro()
        self._stop_creating_or_expanding()
        self._components.ui.assign_paths_to_buttons(self._components.paths)

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

    def _can_end_with(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 1 and self._is_last_station(station)

    def _can_make_loop(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 2 and self._is_first_station(station)

    def _can_add_metro(self) -> bool:
        return len(self._components.metros) < max_num_metros

    def _add_new_metro(self) -> None:
        metro = Metro(self._components.passengers_mediator)
        self.path.add_metro(metro)
        self._components.metros.append(metro)

    def _remove_path_from_network(self) -> None:
        self._components.path_color_manager.release_color_for_path(self.path)
        self._components.paths.remove(self.path)
