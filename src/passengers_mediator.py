from typing import Final, Protocol

from src.entity.holder import Holder
from src.entity.passenger import Passenger
from src.entity.station import Station


class PassengersMediator:
    __slots__ = ("_holders",)

    def __init__(self) -> None:
        self._holders: Final[list[Holder]] = []

    def register(self, holder: Holder) -> None:
        self._holders.append(holder)

    def any_holder_has(self, passenger: Passenger) -> bool:
        return any(passenger in holder.passengers for holder in self._holders)

    def on_passenger_exit(self, source: Holder, passenger: Passenger) -> None:
        if isinstance(source, Station):
            passenger.last_station = source


class PassengersMediatorProtocol(Protocol):

    def register(self, holder: Holder) -> None: ...

    def any_holder_has(self, passenger: Passenger) -> bool: ...

    def on_passenger_exit(self, source: Holder, passenger: Passenger) -> None: ...
