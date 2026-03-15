
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

class BaseRepository(ABC, Generic[TKey, TValue]):
    @abstractmethod
    def get(self, key: TKey) -> TValue | None :
        raise NotImplementedError
    
    @abstractmethod
    def upsert(self, value:TValue) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def delete(self, key: TKey) -> None:
        raise NotImplementedError