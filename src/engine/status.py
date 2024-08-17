class EngineStatus:
    __slots__ = (
        "frame",
        "is_paused",
        "score",
    )

    def __init__(self) -> None:
        self.frame: int = 0
        self.is_paused: bool = False
        self.score: int = 0
