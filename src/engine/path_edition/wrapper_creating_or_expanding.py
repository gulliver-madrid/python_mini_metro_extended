from typing import Generator, Literal

from src.entity import Station

from .creating_or_expanding_base import CreatingOrExpandingPathBase

WrapperCreatingOrExpanding = Generator[
    Literal["exit"] | None, tuple[str, Station | None], None
]


def gen_wrapper_creating_or_expanding(
    creating_or_expanding: CreatingOrExpandingPathBase,
) -> WrapperCreatingOrExpanding:
    assert creating_or_expanding
    # print("\nentering wrapper")

    while True:
        mouse_op, station = yield None
        # print(f"received {mouse_op}")

        match mouse_op:
            case "mouse_motion":
                assert station
                creating_or_expanding.add_station_to_path(station)
            case "mouse_up":
                if station:
                    creating_or_expanding.try_to_end_path_on_station(station)
                else:
                    creating_or_expanding.try_to_end_path_on_last_station()
            case "mouse_down":
                creating_or_expanding.abort_path_creation_or_expanding()
            case _:
                assert False, f"Unknown command: {mouse_op}"

        if not creating_or_expanding:
            break
    # print("\nexiting wrapper")
    yield "exit"
