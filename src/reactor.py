import queue

import pygame

from src.console import Console
from src.engine.engine import Engine
from src.entity.station import Station
from src.event.event import Event
from src.event.keyboard import KeyboardEvent
from src.event.mouse import MouseEvent
from src.event.type import KeyboardEventType, MouseEventType
from src.geometry.point import Point
from src.ui.button import Button
from src.ui.path_button import PathButton


class UI_Reactor:
    __slots__ = (
        "engine",
        "is_mouse_down",
        "_console",
    )

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self._console = Console()
        self.is_mouse_down: bool = False

    def react(self, event: Event | None) -> None:
        if isinstance(event, MouseEvent):
            self._on_mouse_event(event)
        elif isinstance(event, KeyboardEvent):
            self._on_keyboard_event(event)
        # Process console commands
        try:
            cmd = self._console.console_queue.get_nowait()
            if cmd == "resume":
                if self.engine.is_paused:
                    self.engine.toggle_pause()
        except queue.Empty:
            pass

    def _on_mouse_event(self, event: MouseEvent) -> None:
        entity = self.engine.get_containing_entity(event.position)

        if event.event_type == MouseEventType.MOUSE_DOWN:
            self.is_mouse_down = True
            self._on_mouse_down(entity, event.position)

        elif event.event_type == MouseEventType.MOUSE_UP:
            self.is_mouse_down = False
            self._on_mouse_up(entity)

        elif event.event_type == MouseEventType.MOUSE_MOTION:
            self._on_mouse_motion(entity, event.position)

    def _on_keyboard_event(self, event: KeyboardEvent) -> None:
        if event.event_type == KeyboardEventType.KEY_DOWN:
            if event.key == pygame.K_SPACE:
                self.engine.toggle_pause()
            if event.key == pygame.K_t:
                if self.engine.is_paused:
                    self.engine.toggle_pause()
                self.engine.steps_allowed = 1
            elif event.key == pygame.K_ESCAPE:
                self.engine.exit()
            elif event.key == pygame.K_c:
                if not self.engine.is_paused:
                    self.engine.toggle_pause()
                self._console.launch_console(self.engine)
            elif event.key == pygame.K_d:
                self.engine.showing_debug = not self.engine.showing_debug
            elif event.key == pygame.K_s:
                if self.engine.game_speed == 1:
                    self.engine.game_speed = 5
                else:
                    self.engine.game_speed = 1

    def _on_mouse_motion(
        self, entity: Station | PathButton | None, position: Point
    ) -> None:
        self.engine.ui.last_pos = position
        if self.is_mouse_down:
            self._on_mouse_motion_with_mouse_down(entity, position)
        elif isinstance(entity, Button):
            entity.on_hover()
        else:
            self.engine.ui.exit_buttons()

    def _on_mouse_down(
        self, entity: Station | PathButton | None, position: Point
    ) -> None:
        if isinstance(entity, Station):
            self.engine.path_manager.start_path_on_station(entity)
        if not entity:
            self.engine.try_starting_path_edition(position)

    def _on_mouse_up(self, entity: Station | PathButton | None) -> None:
        if self.engine.path_manager.path_being_created:
            if isinstance(entity, Station):
                self.engine.path_manager.end_path_on_station(entity)
            else:
                self.engine.path_manager.end_path_on_last_station()
        elif isinstance(entity, PathButton) and entity.path:
            self.engine.path_manager.remove_path(entity.path)

    def _on_mouse_motion_with_mouse_down(
        self, entity: Station | PathButton | None, position: Point
    ) -> None:
        if self.engine.path_manager.path_being_created:
            if isinstance(entity, Station):
                self.engine.path_manager.add_station_to_path(entity)
            else:
                self.engine.path_manager.set_temporary_point(position)
