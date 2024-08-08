from src.engine.game_components import GameComponents
from src.engine.path_being_created_or_expanded_base import (
    PathBeingCreatedOrExpandedBase,
)
from src.entity.path import Path
from src.entity.station import Station


class PathBeingCreated(PathBeingCreatedOrExpandedBase):
    """Creating"""

    __slots__ = ()

    def __init__(self, components: GameComponents, path: Path):
        super().__init__(components, path)
        assert not self.is_expanding
        assert self._from_end

    def add_station_to_path(self, station: Station) -> None:
        assert self.is_active

        self._add_station_to_path(station)
        if self.path.is_looped:
            self._finish_path_creation()

    def try_to_end_path_on_station(self, station: Station) -> None:
        """
        The station should be in the path already, we are going to end path creation.
        """
        assert self.is_active
        path = self.path
        if station not in path.stations:
            self.abort_path_creation_or_expanding()
            return

        # the loop should have been detected in `add_station_to_path` method
        assert not self._can_make_loop(station)

        assert self._is_last_station(station)  # test
        if self._can_end_with(station):
            self._finish_path_creation()
        else:
            self.abort_path_creation_or_expanding()

    def abort_path_creation_or_expanding(self) -> None:
        assert self.is_active
        self._remove_path_from_network()
        self._stop_creating_or_expanding()

    def _add_station_to_path(self, station: Station) -> bool:
        """
        Returns True if it should be inserted at start instead
        """
        self._add_station_to_path_from_end(station)
        return False
