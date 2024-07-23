class MediatorStatus:
    __slots__ = (
        "is_paused",
        "score",
    )

    def __init__(self) -> None:
        self.is_paused: bool = False
        self.score: int = 0
