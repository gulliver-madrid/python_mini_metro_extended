from src.engine.game_components import GameComponents
from src.engine.path_being_created_or_expanded_base import (
    PathBeingCreatedOrExpandedBase,
)
from src.entity.path import Path
from src.entity.station import Station


class PathBeingExpanded(PathBeingCreatedOrExpandedBase):
    """Expanding"""

    __slots__ = ()

    def __init__(self, components: GameComponents, path: Path, station: Station):
        super().__init__(components, path, station)
        assert self.is_expanding

    def add_station_to_path(self, station: Station) -> None:
        assert self.is_active

        if station in self.path.stations:
            return
        should_insert = self._add_station_to_path(station)
        if should_insert:
            self._insert_station(station, 0)
        assert self.is_active
        assert self.is_expanding
        self._stop_creating_or_expanding()
        # TODO: allow adding more than one station when expanding

    def try_to_end_path_on_station(self, station: Station) -> None:
        """
        The station should be in the path already, we are going to end path creation.
        """
        assert self.is_active
        path = self.path
        if station not in path.stations:
            self.abort_path_creation_or_expanding()
            return
        self._stop_creating_or_expanding()

    def abort_path_creation_or_expanding(self) -> None:
        assert self.is_active
        self._stop_creating_or_expanding()

    def _add_station_to_path(self, station: Station) -> bool:
        """Returns True if it should be inserted at start instead"""
        # TODO: improve this, avoid having to return a boolean
        if not self._from_end:
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

        self._add_station_to_path_from_end(station)
        return False
