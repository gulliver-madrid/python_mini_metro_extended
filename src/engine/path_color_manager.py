from typing import Final

from src.config import max_num_paths
from src.entity import Path
from src.type import Color
from src.utils import hue_to_rgb


class PathColorManager:
    __slots__ = (
        "_path_colors",
        "_color_status",  # color being taken or not
    )

    def __init__(self) -> None:
        self._color_status: Final[dict[Path, Color]] = {}
        self._path_colors: Final[dict[Color, bool]] = self._get_initial_path_colors()

    def assign_color_to_path(self, color: Color, path: Path) -> None:
        self._color_status[path] = color
        self._path_colors[color] = True

    def get_first_path_color_available(self) -> Color | None:
        assigned_color: Color | None = None
        for path_color, taken in self._path_colors.items():
            if taken:
                continue
            assigned_color = path_color
            break
        return assigned_color

    def release_color_for_path(self, path: Path) -> None:
        self._path_colors[path.color] = False
        del self._color_status[path]

    #######################
    ### private methods ###
    #######################

    def _get_initial_path_colors(self) -> dict[Color, bool]:
        path_colors: Final[dict[Color, bool]] = {}
        for i in range(max_num_paths):
            color = hue_to_rgb(i / (max_num_paths + 1))
            path_colors[color] = False  # not taken
        return path_colors
