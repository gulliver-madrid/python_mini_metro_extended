from dataclasses import dataclass, field
from typing import Final

from ..segments import Segment


@dataclass
class PathState:
    segments: Final[list[Segment]] = field(init=False, default_factory=list)
    is_looped: bool = field(init=False, default=False)
