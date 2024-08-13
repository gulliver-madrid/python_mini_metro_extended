from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from src.entity.passenger import Passenger

if TYPE_CHECKING:
    from src.entity.holder import Holder


class PassengersMediatorProtocol(Protocol):

    def register(self, holder: Holder) -> None: ...

    def on_new_passenger_added(self, passenger: Passenger) -> None: ...

    def on_passenger_exit(self, source: Holder, passenger: Passenger) -> None: ...
