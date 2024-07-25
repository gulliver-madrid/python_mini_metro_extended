from typing import Final

from src.geometry.type import ShapeType

# game
framerate = 60

# screen
screen_color = (255, 255, 255)

# station
num_stations = 10
station_size = 60
station_capacity = 12
station_color = (0, 0, 0)
station_shape_type_list = [
    ShapeType.RECT,
    ShapeType.CIRCLE,
    ShapeType.TRIANGLE,
    ShapeType.CROSS,
]
station_passengers_per_row = 4

# passenger
passenger_size = 10
passenger_color = (128, 128, 128)
passenger_display_buffer = 1.5 * passenger_size


class _PassengerSpawningConfig:
    first_time_divisor: Final = 3
    interval_step: Final = 8


# metro
max_num_metros = 6
metro_size = 30
metro_color = (200, 200, 200)
metro_capacity = 6
metro_speed_per_ms = 150 / 1000  # pixels / ms
metro_passengers_per_row = 3

# path
max_num_paths = 5
path_width = 10
path_order_shift = path_width

# button
button_color = (180, 180, 180)
button_size = 30

# path button
path_button_buffer = 20
path_button_dist_to_bottom = 50
path_button_start_left = 500
path_button_cross_size = 25
path_button_cross_width = 5

# gui
gui_height_proportion = 0.12

# text
score_font_size = 50
score_display_coords = (20, 20)

# debug
_unfilled_shapes = False
_padding_segments_color: tuple[int, int, int] | None = None


class Config:
    # screen
    screen_width = 1600
    screen_height = 840
    # components
    passenger_spawning = _PassengerSpawningConfig
    # debug
    unfilled_shapes = _unfilled_shapes
    padding_segments_color = _padding_segments_color
