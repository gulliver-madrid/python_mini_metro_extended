from abc import ABC, abstractmethod
from typing import Final

from .ids import EntityId


class Entity(ABC):
    _id: Final[EntityId]

    def __init__(self, id: EntityId):
        self._id = id

    @property
    @abstractmethod
    def id(self) -> EntityId:
        return self._id
