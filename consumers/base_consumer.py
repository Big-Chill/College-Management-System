from abc import ABC, abstractmethod

class IBaseConsumer(ABC):
    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def consume(self):
        pass