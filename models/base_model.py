from abc import ABC, abstractmethod
from typing import Dict

class IModel(ABC):
    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def validate_and_prepare_data(self, payload: Dict) -> Dict:
        pass
