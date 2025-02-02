import pygame

from src.config import Config
from src.console import Console
from src.engine.engine import Engine
from src.engine.path_edition import WrapperCreatingOrExpanding
from src.entity.station import Station
from src.event.event import Event
from src.event.keyboard import KeyboardEvent
from src.event.mouse import MouseEvent
from src.event.type import KeyboardEventType, MouseEventType
from src.geometry.point import Point
from src.gui.button import Button
from src.gui.path_button import PathButton


class UI_Reactor:
    __slots__ = (
        "_engine",
        "is_mouse_down",
        "_console",
        "_last_clicked",
        "_index_clicked",
        "wrapper_creating_or_expanding",
    )

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._console = Console()
        self.is_mouse_down: bool = False
        self._last_clicked: Station | None = None
        self._index_clicked = 0
        self.wrapper_creating_or_expanding: WrapperCreatingOrExpanding | None = None

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
        self,
        entity: Station | PathButton | None,
        position: Point,
    ) -> None:
        if self._last_clicked:
            self._last_clicked = None
        self._engine.gui.last_pos = position
        if self.is_mouse_down:
            self._on_mouse_motion_with_mouse_down(entity, position)
        else:
            self._on_mouse_motion_with_mouse_up(entity)

    def _on_mouse_down(
        self, entity: Station | PathButton | None, position: Point
    ) -> None:
        if self.wrapper_creating_or_expanding:
            self._send_to_wrapper_creating_or_expanding("mouse_down", entity)

        elif isinstance(entity, Station):
            if self._last_clicked == entity:
                self._index_clicked += 1
            else:
                self._index_clicked = 0
                self._last_clicked = entity

            paths = self._engine.path_manager.get_paths_with_station(entity)

            allow_creating_new_path = self._engine.max_paths_reached()

            num_possible_targets = len(paths) + allow_creating_new_path
            if not num_possible_targets:
                return
            index_clicked = self._index_clicked % num_possible_targets

            if not allow_creating_new_path:
                index_clicked += 1

            if index_clicked == 0:
                self.wrapper_creating_or_expanding = (
                    self._engine.path_manager.start_path_on_station(entity)
                )
            else:
                self.wrapper_creating_or_expanding = (
                    self._engine.path_manager.start_expanding_path_on_station(
                        entity, index_clicked - 1
                    )
                )

            assert self.wrapper_creating_or_expanding
            next(self.wrapper_creating_or_expanding)

        elif (
            not entity
            and self._engine.is_paused
            and not Config.allow_self_crossing_lines
        ):
            self._engine.try_starting_path_edition(position)

    def _on_mouse_up(self, entity: Station | PathButton | None) -> None:
        path_manager = self._engine.path_manager
        if self.wrapper_creating_or_expanding:
            self._send_to_wrapper_creating_or_expanding("mouse_up", entity)
        elif path_manager.editing_intermediate_stations:
            path_manager.stop_edition()
        elif isinstance(entity, PathButton) and entity.path:
            path_manager.remove_path(entity.path)

    def _on_mouse_motion_with_mouse_down(
        self,
        entity: Station | PathButton | None,
        position: Point,
    ) -> None:
        path_manager = self._engine.path_manager
        if isinstance(entity, Station):
            if self.wrapper_creating_or_expanding:
                self._send_to_wrapper_creating_or_expanding("mouse_motion", entity)

            elif path_manager.editing_intermediate_stations:
                path_manager.touch(entity)
        else:
            path_manager.try_to_set_temporary_point(position)

    def _on_mouse_motion_with_mouse_up(
        self, entity: Station | PathButton | None
    ) -> None:
        if isinstance(entity, Button):
            entity.on_hover()
        else:
            self._engine.gui.exit_buttons()

    def _send_to_wrapper_creating_or_expanding(
        self, command: str, entity: Station | object
    ) -> None:
        assert self.wrapper_creating_or_expanding
        station = entity if isinstance(entity, Station) else None
        result = self.wrapper_creating_or_expanding.send((command, station))
        if result == "exit":
            self.wrapper_creating_or_expanding = None
