# app/repositories/__init__.py
from abc import ABC, abstractmethod

class IDBRepository(ABC):
    @abstractmethod
    def insert(self, table: str, data: dict):
        pass

    @abstractmethod
    def select(self, table: str, conditions: str):
        pass

    @abstractmethod
    def remove_all_data(self):
        pass
