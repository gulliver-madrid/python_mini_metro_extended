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
)
function_exclude_patterns = (
    "draw",
    "update_segments",
    "render",
    "increment_time",
)
