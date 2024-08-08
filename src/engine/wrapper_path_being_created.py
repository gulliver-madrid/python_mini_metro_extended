from typing import Generator, Literal

from src.entity import Station

from .path_being_created import PathBeingCreatedOrExpanding

WrapperCreatingOrExpanding = Generator[
    Literal["exit"] | None, tuple[str, Station | None], None
]


def gen_wrapper_creating_or_expanding(
    path_being_created: PathBeingCreatedOrExpanding,
) -> WrapperCreatingOrExpanding:
    assert path_being_created

    while True:
        mouse_op, station = yield None

        match mouse_op:
            case "mouse_motion":
                assert isinstance(station, Station)
                path_being_created.add_station_to_path(station)
            case "mouse_up":
                if isinstance(station, Station):
                    path_being_created.try_to_end_path_on_station(station)
                else:
                    path_being_created.try_to_end_path_on_last_station()
            case "mouse_down":
                path_being_created.abort_path_creation_or_expanding()
            case _:
                assert False, f"Unknown command: {mouse_op}"

        if not path_being_created:
            break

    yield "exit"
