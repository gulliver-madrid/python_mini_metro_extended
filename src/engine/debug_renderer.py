from collections.abc import Sequence
from typing import Final

import pygame

from src.config import Config
from src.engine.game_components import GameComponents
from src.entity import Passenger
from src.geometry.point import Point

from .passenger_spawner import TravelPlansMapping

LINE_HEIGHT = 30
DEFAULT_SIZE = (300, 300)


class DebugRenderer:
    __slots__ = (
        "_debug_surf",
        "_size",
        "_components",
    )

    fg_color: Final = (255, 255, 255)
    bg_color: Final = (0, 0, 0)

    def __init__(self, components: GameComponents) -> None:
        self._components = components
        self._size = DEFAULT_SIZE

    @property
    def _position(self) -> Point:
        w, h = self._size
        return Point(
            Config.screen_width - w,
            Config.screen_height - h,
        )

    def draw_debug(
        self,
        screen: pygame.surface.Surface,
        is_creating_path: bool,
        passengers: Sequence[Passenger],
        travel_plans: TravelPlansMapping,
        ms_until_next_spawn: float,
        speed: float,
    ) -> None:
        gui = self._components.gui
        font = gui.small_font
        mouse_pos = gui.last_pos
        fps = gui.clock.get_fps() if gui.clock else None

        debug_texts = self._define_debug_texts(
            mouse_pos,
            fps,
            passengers,
            travel_plans,
            ms_until_next_spawn=ms_until_next_spawn,
            is_creating_path=is_creating_path,
            game_speed=speed,
        )
        number_of_lines = len(debug_texts)

        self._size = (self._size[0], (number_of_lines + 1) * LINE_HEIGHT)
        self._debug_surf = pygame.Surface(self._size)
        self._debug_surf.set_alpha(180)
        self._debug_surf.fill(self.bg_color)

        self._draw_debug_texts(debug_texts, font, self.fg_color)

        screen.blit(
            self._debug_surf,
            self._position.to_tuple(),
        )

    def _define_debug_texts(
        self,
        mouse_pos: Point | None,
        fps: float | None,
        passengers: Sequence[Passenger],
        travel_plans: TravelPlansMapping,
        *,
        ms_until_next_spawn: float,
        is_creating_path: bool,
        game_speed: float,
    ) -> list[str]:
        debug_texts: list[str] = []
        if mouse_pos:
            debug_texts.append(f"Mouse position: {mouse_pos.to_tuple()}")
        debug_texts.append(f"Game time: {self._components.status.game_time}")
        if fps:
            debug_texts.append(f"FPS: {fps:.1f}")
        debug_texts.append(f"Game speed: {game_speed:.2f}")
        debug_texts.append(f"Number of passengers: {len(passengers)}")
        debug_texts.append(f"Number of travel plans: {len(travel_plans)}")
        debug_texts.append(f"Until next spawning: { ( ms_until_next_spawn/1000):.1f}")
        debug_texts.append(f"Is creating path: { ( is_creating_path)}")
        return debug_texts

    def _draw_debug_texts(
        self,
        debug_texts: list[str],
        font: pygame.font.Font,
        fg_color: tuple[int, int, int],
    ) -> None:
        for i, text in enumerate(debug_texts):
            debug_label = font.render(text, True, fg_color)
            self._debug_surf.blit(debug_label, (10, 10 + i * LINE_HEIGHT))
