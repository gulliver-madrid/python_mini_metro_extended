exclude_patterns: tuple[str, ...] = (
    "_bootstrap",
    "site-packages",
    "AppData",
    "<string>",
)

custom_exclude_patterns = (
    "src/geometry",
    "game_renderer",
    "graph",
    "convert.py",
)

function_exclude_patterns = (
    "draw",
    "update_segments",
    "render",
    "increment_time",
    "get_containing_entity",
    "exit_buttons",
    "get_random_stations",
    "_try_process_console_commands",
)
