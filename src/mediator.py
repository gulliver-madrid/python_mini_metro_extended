from collections import defaultdict
from typing import Final, Sequence

from src.entity.holder import Holder
from src.entity.metro import Metro
from src.entity.passenger import Passenger
from src.entity.station import Station


class Mediator:
    _passengers: Final[dict[Holder, list[Passenger]]]

    def __init__(self) -> None:
        self._passengers = defaultdict(list)

    ######################
    ### public methods ###
    ######################

    def get_passengers_in_holder(self, holder: Holder) -> Sequence[Passenger]:
        return self._passengers[holder]

    def get_holder_occupation(self, holder: Holder) -> int:
        return len(self._passengers[holder])

    def holder_has_room(self, holder: Holder) -> bool:
        return holder.capacity > holder.occupation

    def add_new_passenger_to_holder(self, holder: Holder, passenger: Passenger) -> None:
        assert all(
            passenger not in passengers for passengers in self._passengers.values()
        )
        self._add_passenger_to_holder(holder, passenger)

    def passenger_arrives(self, holder: Holder, passenger: Passenger) -> None:
        assert isinstance(holder, Metro)
        assert passenger in self._passengers[holder]
        self._remove_passenger_from_holder(holder, passenger)

    def move_passenger(
        self, passenger: Passenger, source: Holder, dest: Holder
    ) -> None:
        if isinstance(source, Station):
            passenger.last_station = source
        self._add_passenger_to_holder(dest, passenger)
        self._remove_passenger_from_holder(source, passenger)

    #######################
    ### private methods ###
    #######################

    def _add_passenger_to_holder(self, holder: Holder, passenger: Passenger) -> None:
        assert holder.has_room()
        self._passengers[holder].append(passenger)

    def _remove_passenger_from_holder(
        self, holder: Holder, passenger: Passenger
    ) -> None:
        assert passenger in self._passengers[holder]
        self._passengers[holder].remove(passenger)
