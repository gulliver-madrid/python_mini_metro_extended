from dataclasses import dataclass, field
from typing import Final

from ..metro import Metro
from ..segments import Segment


@dataclass
class PathState:
    segments: Final[list[Segment]] = field(init=False, default_factory=list)
    is_looped: bool = field(init=False, default=False)

    def update_metro_current_segment(self, metro: Metro) -> None:
        metro.current_segment = self.segments[metro.current_segment_idx]
