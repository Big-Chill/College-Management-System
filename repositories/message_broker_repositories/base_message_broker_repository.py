# app/repositories/message_broker_repositories/__init__.py
from abc import ABC, abstractmethod

class IMessageBrokerRepository(ABC):
    @abstractmethod
    def publish(self, topic: str, message: dict):
        pass

    @abstractmethod
    def subscribe(self, topic: str, callback):
        pass

    @abstractmethod
    def close(self):
        pass