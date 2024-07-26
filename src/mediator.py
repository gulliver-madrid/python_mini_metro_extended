from collections import defaultdict
from typing import Final, Sequence

from src.entity.holder import Holder
from src.entity.passenger import Passenger


class Mediator:
    _passengers: Final[dict[Holder, list[Passenger]]]

    def __init__(self) -> None:
        self._passengers = defaultdict(list)

    def get_passengers(self, holder: Holder) -> Sequence[Passenger]:
        return self._passengers[holder]

    def get_num_passengers(self, holder: Holder) -> int:
        return len(self._passengers[holder])

    def add_passenger_to_holder(self, holder: Holder, passenger: Passenger) -> None:
        assert holder.has_room()
        self._passengers[holder].append(passenger)

    def remove_passenger_from_holder(
        self, holder: Holder, passenger: Passenger
    ) -> None:
        assert passenger in self._passengers[holder]
        self._passengers[holder].remove(passenger)

    def move_passenger(
        self, passenger: Passenger, source: Holder, dest: Holder
    ) -> None:
        assert dest.has_room()
        dest.add_passenger(passenger)
        source.remove_passenger(passenger)
