from dependency_injector import containers, providers
from .database_container import DatabaseContainer
from .message_broker_container import MessageBrokerContainer
import configuration

class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    database_container = providers.Container(DatabaseContainer)
    message_broker_container = providers.Container(MessageBrokerContainer)