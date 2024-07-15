import pygame

from src.entity.station import Station
from src.event.event import Event
from src.event.keyboard import KeyboardEvent
from src.event.mouse import MouseEvent
from src.event.type import KeyboardEventType, MouseEventType
from src.geometry.point import Point
from src.mediator.mediator import Mediator
from src.ui.button import Button
from src.ui.path_button import PathButton


class UI_Reactor:
    __slots__ = (
        "mediator",
        "is_mouse_down",
    )

    def __init__(self, mediator: Mediator) -> None:
        self.mediator = mediator
        self.is_mouse_down: bool = False

    def react(self, event: Event | None) -> None:
        if isinstance(event, MouseEvent):
            self._on_mouse_event(event)
        elif isinstance(event, KeyboardEvent):
            self._on_keyboard_event(event)

    def _on_mouse_event(self, event: MouseEvent) -> None:
        entity = self.mediator.get_containing_entity(event.position)

        if event.event_type == MouseEventType.MOUSE_DOWN:
            self.is_mouse_down = True
            self._on_mouse_down(entity)

        elif event.event_type == MouseEventType.MOUSE_UP:
            self.is_mouse_down = False
            self._on_mouse_up(entity)

        elif event.event_type == MouseEventType.MOUSE_MOTION:
            self._on_mouse_motion(entity, event.position)

    def _on_keyboard_event(self, event: KeyboardEvent) -> None:
        if event.event_type == KeyboardEventType.KEY_UP:
            if event.key == pygame.K_SPACE:
                self.mediator.toggle_pause()
            elif event.key == pygame.K_ESCAPE:
                self.mediator.exit()

    def _on_mouse_motion(
        self, entity: Station | PathButton | None, position: Point
    ) -> None:
        if self.is_mouse_down:
            self._on_mouse_motion_with_mouse_down(entity, position)
        elif isinstance(entity, Button):
            entity.on_hover()
        else:
            self.mediator.ui.exit_buttons()

    def _on_mouse_down(self, entity: Station | PathButton | None) -> None:
        if isinstance(entity, Station):
            self.mediator.start_path_on_station(entity)

    def _on_mouse_up(self, entity: Station | PathButton | None) -> None:
        if self.mediator.is_creating_path:
            assert self.mediator.path_being_created is not None
            if isinstance(entity, Station):
                self.mediator.end_path_on_station(entity)
            else:
                self.mediator.abort_path_creation()
        elif isinstance(entity, PathButton) and entity.path:
            self.mediator.remove_path(entity.path)

    def _on_mouse_motion_with_mouse_down(
        self, entity: Station | PathButton | None, position: Point
    ) -> None:
        if self.mediator.is_creating_path and self.mediator.path_being_created:
            if isinstance(entity, Station):
                self.mediator.add_station_to_path(entity)
            else:
                self.mediator.path_being_created.path.set_temporary_point(position)
