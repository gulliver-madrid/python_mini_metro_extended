class EngineStatus:
    __slots__ = (
        "game_time",
        "is_paused",
        "score",
    )

    def __init__(self) -> None:
        self.game_time: int = 0
        self.is_paused: bool = False
        self.score: int = 0
