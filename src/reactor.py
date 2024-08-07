import pygame

from src.config import Config
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
        "_engine",
        "is_mouse_down",
        "_console",
        "_last_clicked",
        "_index_clicked",
    )

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._console = Console()
        self.is_mouse_down: bool = False
        self._last_clicked: Station | None = None
        self._index_clicked = 0

    def react(self, event: Event | None) -> None:
        if isinstance(event, MouseEvent):
            self._on_mouse_event(event)
        elif isinstance(event, KeyboardEvent):
            self._on_keyboard_event(event)
        self._try_process_console_commands()

    def _try_process_console_commands(self) -> None:
        cmd = self._console.try_get_command()
        if cmd == "resume":
            if self._engine.is_paused:
                self._engine.toggle_pause()
        else:
            assert cmd is None, cmd

    def _on_mouse_event(self, event: MouseEvent) -> None:
        entity = self._engine.get_containing_entity(event.position)

        match event.event_type:
            case MouseEventType.MOUSE_DOWN:
                self.is_mouse_down = True
                self._on_mouse_down(entity, event.position)
            case MouseEventType.MOUSE_UP:
                self.is_mouse_down = False
                self._on_mouse_up(entity)
            case MouseEventType.MOUSE_MOTION:
                self._on_mouse_motion(entity, event.position)
            case _:
                pass

    def _on_keyboard_event(self, event: KeyboardEvent) -> None:
        if event.event_type != KeyboardEventType.KEY_DOWN:
            return

        match event.key:
            case pygame.K_SPACE:
                self._engine.toggle_pause()
            case pygame.K_t:
                # step by step
                if self._engine.is_paused:
                    self._engine.toggle_pause()
                self._engine.steps_allowed = 1
            case pygame.K_ESCAPE:
                self._engine.exit()
            case pygame.K_c:
                if not self._engine.is_paused:
                    self._engine.toggle_pause()
                self._console.launch_console(self._engine)
            case pygame.K_d:
                self._engine.showing_debug = not self._engine.showing_debug
            case pygame.K_s:
                if self._engine.game_speed == 1:
                    self._engine.game_speed = 5
                else:
                    self._engine.game_speed = 1
            case _:
                pass

    def _on_mouse_motion(
        self, entity: Station | PathButton | None, position: Point
    ) -> None:
        if self._last_clicked:
            self._last_clicked = None
        self._engine.ui.last_pos = position
        if self.is_mouse_down:
            self._on_mouse_motion_with_mouse_down(entity, position)
        elif isinstance(entity, Button):
            entity.on_hover()
        else:
            self._engine.ui.exit_buttons()

    def _on_mouse_down(
        self, entity: Station | PathButton | None, position: Point
    ) -> None:
        if self._engine.path_manager.path_being_created:
            self._engine.path_manager.abort_path_creation_or_expanding()
        if isinstance(entity, Station):
            if self._last_clicked == entity:
                self._index_clicked += 1
            else:
                self._index_clicked = 0
                self._last_clicked = entity

            paths = self._engine.path_manager.get_paths_with_station(entity)

            num_possible_targets = len(paths) + 1
            index_clicked = self._index_clicked % num_possible_targets

            if index_clicked == 0:
                self._engine.path_manager.start_path_on_station(entity)
            else:
                self._engine.path_manager.start_expanding_path_on_station(
                    entity, index_clicked - 1
                )

        if (
            not entity
            and self._engine.is_paused
            and not Config.allow_self_crossing_lines
        ):
            self._engine.try_starting_path_edition(position)

    def _on_mouse_up(self, entity: Station | PathButton | None) -> None:
        path_manager = self._engine.path_manager
        if path_manager.path_being_created:
            if isinstance(entity, Station):
                path_manager.try_to_end_path_on_station(entity)
            else:
                path_manager.try_to_end_path_on_last_station()

        elif path_manager.editing_intermediate_stations:
            path_manager.stop_edition()
        elif isinstance(entity, PathButton) and entity.path:
            path_manager.remove_path(entity.path)

    def _on_mouse_motion_with_mouse_down(
        self, entity: Station | PathButton | None, position: Point
    ) -> None:
        if self._engine.path_manager.path_being_created:
            if isinstance(entity, Station):
                self._engine.path_manager.add_station_to_path(entity)
            else:
                self._engine.path_manager.set_temporary_point(position)
        elif self._engine.path_manager.editing_intermediate_stations:
            self._engine.path_manager.editing_intermediate_stations.set_temporary_point(
                position
            )
            if isinstance(entity, Station):
                self._engine.path_manager.touch(entity)
