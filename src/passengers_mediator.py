from typing import Final

from src.entity.holder import Holder
from src.entity.passenger import Passenger
from src.entity.station import Station
from src.exceptions import GameException


class PassengersMediator:
    __slots__ = ("_holders",)

    def __init__(self) -> None:
        self._holders: Final[list[Holder]] = []

    ######################
    ### public methods ###
    ######################

    def register(self, holder: Holder) -> None:
        self._holders.append(holder)

    def on_new_passenger_added(self, passenger: Passenger) -> None:
        if self._any_holder_has(passenger):
            raise GameException(
                "Passengers can be in more than one Holder at the same time"
            )

    def on_passenger_exit(self, source: Holder, passenger: Passenger) -> None:
        if isinstance(source, Station):
            passenger.last_station = source

    #######################
    ### private methods ###
    #######################
    def _any_holder_has(self, passenger: Passenger) -> bool:
        return any(passenger in holder.passengers for holder in self._holders)
