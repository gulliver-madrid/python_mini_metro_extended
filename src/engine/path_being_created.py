from __future__ import annotations

from typing import Final

from src.config import Config, max_num_metros
from src.engine.utils import update_metros_segment_idx
from src.entity import Path, Station
from src.entity.metro import Metro

from .game_components import GameComponents


class PathBeingCreatedOrExpanding:
    """Created or expanding"""

    __slots__ = (
        "path",
        "is_active",
        "_components",
        "is_expanding",  # it can be edition or creation
        "_from_end",
    )

    def __init__(
        self, components: GameComponents, path: Path, station: Station | None = None
    ):
        self.path: Final = path
        self.is_active = True
        self._components: Final = components
        self.is_expanding: Final = station is not None
        self._set_from_end_value(station is None or not self._is_first_station(station))

    def __bool__(self) -> bool:
        return self.is_active

    ######################
    ### public methods ###
    ######################

    def add_station_to_path(self, station: Station) -> None:
        assert self.is_active
        if self.is_expanding:
            if station not in self.path.stations:
                should_insert = self._add_station_to_path(station)
                if should_insert:
                    self._insert_station(station, 0)
                assert self.is_active
                assert self.is_expanding
                self.path.remove_temporary_point()
                self._stop_creating_or_expanding()
                # TODO: allow adding more than one station when expanding
            return
        self._add_station_to_path(station)
        if self.path.is_looped:
            self._finish_path_creation()

    def try_to_end_path_on_station(self, station: Station) -> None:
        """
        The station should be in the path already, we are going to end path creation.
        """
        assert self.is_active
        path = self.path
        assert (
            station in path.stations
        ), "The logic should have been executed when the mouse moved into the station."
        if self.is_expanding:
            self._stop_creating_or_expanding()
            return

        # the loop should have been detected in `add_station_to_path` method
        assert not self._can_make_loop(station)

        assert self._is_last_station(station)  # TODO: fix private access  # test
        if self._can_end_with(station):
            self._finish_path_creation()
        else:
            self.abort_path_creation_or_expanding()

    def try_to_end_path_on_last_station(self) -> None:
        assert self.is_active
        last = self.path.stations[-1]
        self.try_to_end_path_on_station(last)

    def abort_path_creation_or_expanding(self) -> None:
        assert self.is_active
        if not self.is_expanding:
            self._components.path_color_manager.release_color_for_path(self.path)
            self._components.paths.remove(self.path)
        self._stop_creating_or_expanding()

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

    def _add_station_to_path(self, station: Station) -> bool:
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
        self.path.remove_temporary_point()
        if len(self._components.metros) < max_num_metros:
            metro = Metro(self._components.passengers_mediator)
            self.path.add_metro(metro)
            self._components.metros.append(metro)
        self._stop_creating_or_expanding()
        self._components.ui.assign_paths_to_buttons(self._components.paths)

    def _stop_creating_or_expanding(self) -> None:
        assert self.is_active
        self.path.selected = False
        self.is_active = False

    def _num_stations_in_this_path(self) -> int:
        return len(self.path.stations)

    def _is_first_station(self, station: Station) -> bool:
        return self.path.stations[0] == station

    def _is_last_station(self, station: Station) -> bool:
        return self.path.stations[-1] == station

    def _can_end_with(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 1 and self._is_last_station(station)

    def _can_make_loop(self, station: Station) -> bool:
        return self._num_stations_in_this_path() > 2 and self._is_first_station(station)

    def _set_from_end_value(self, value: bool) -> None:
        self._from_end = value
        self.path.temp_point_is_from_end = value
