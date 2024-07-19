from abc import ABC, abstractmethod
from collections import defaultdict
from typing import ClassVar, Final

from .ids import EntityId, EntityNumId


class Entity(ABC):
    _id: Final[EntityId]
    _num_ids: ClassVar[dict[str, int]] = defaultdict(int)

    def __init__(self, id: EntityId):
        self._id = id
        this_class = type(self)
        self._num_id = EntityNumId(this_class._num_ids[this_class.__name__])
        this_class._num_ids[this_class.__name__] += 1

    @property
    @abstractmethod
    def id(self) -> EntityId:
        return self._id

    @property
    def num_id(self) -> EntityNumId:
        return self._num_id

    def __repr__(self) -> str:
        return f"{type(self).__name__}-{self.num_id}"
