"""Tests only methods"""

import pygame

from src.engine.engine import Engine
from src.entity.passenger import Passenger
from src.entity.path.path import Path
from src.entity.segments.segment import Segment
from src.entity.station import Station
from src.protocols.passenger_mediator import PassengersMediatorProtocol


def legacy_get_engine_passengers(engine: Engine) -> list[Passenger]:
    return engine._components.passengers  # pyright: ignore [reportPrivateUsage]


def legacy_get_engine_paths(engine: Engine) -> list[Path]:
    return engine._components.paths  # pyright: ignore [reportPrivateUsage]


def legacy_get_engine_stations(engine: Engine) -> list[Station]:
    return engine._components.stations  # pyright: ignore [reportPrivateUsage]


def legacy_get_engine_passengers_mediator(engine: Engine) -> PassengersMediatorProtocol:
    return (
        engine._components.passengers_mediator  # pyright: ignore [reportPrivateUsage]
    )


def legacy_path_segments(path: Path) -> list[Segment]:
    return path._state.segments  # pyright: ignore [reportPrivateUsage]


def legacy_path_draw_with_order(
    path: Path, surface: pygame.surface.Surface, path_order: int
) -> None:

    path._path_order = path_order  # pyright: ignore [reportPrivateUsage]
    path.draw(surface)
