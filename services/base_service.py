# app/repositories/__init__.py
from abc import ABC, abstractmethod

class IService(ABC):
    @abstractmethod
    def validate_data(self, data: dict, in_loop: bool = False) -> dict:
        pass