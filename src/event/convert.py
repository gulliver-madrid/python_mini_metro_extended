from typing import Final
import pygame

from src.geometry.point import Point
from src.event.event import Event
from src.event.keyboard import KeyboardEvent
from src.event.mouse import MouseEvent
from src.event.type import KeyboardEventType, MouseEventType
from src.utils import tuple_to_point

NULL_POS: Final = (0, 0)

null_point: Final = tuple_to_point(NULL_POS)
last_mouse_pos: Point = null_point


def convert_pygame_event(event: pygame.event.Event) -> Event | None:
    global last_mouse_pos
    if event.type != pygame.MOUSEMOTION:
        print(event)

    match event.type:
        case pygame.MOUSEBUTTONDOWN:
            mouse_position = tuple_to_point(event.pos)
            return MouseEvent(MouseEventType.MOUSE_DOWN, mouse_position)
        case pygame.MOUSEBUTTONUP:
            mouse_position = tuple_to_point(event.pos)
            return MouseEvent(MouseEventType.MOUSE_UP, mouse_position)
        case pygame.MOUSEMOTION:
            mouse_position = tuple_to_point(event.pos)
            last_mouse_pos = mouse_position
            return MouseEvent(MouseEventType.MOUSE_MOTION, mouse_position)
        case pygame.KEYUP:
            return KeyboardEvent(KeyboardEventType.KEY_UP, event.key)
        case pygame.KEYDOWN:
            return KeyboardEvent(KeyboardEventType.KEY_DOWN, event.key)
        case _:
            return None
