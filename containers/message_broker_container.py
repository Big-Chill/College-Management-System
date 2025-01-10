# from configuration import KAFKA_HOST, KAFKA_AUTO_OFFSET_RESET, KAFKA_GROUP_ID
from dependency_injector import containers, providers
from repositories import KafkaRepository
from kafka import KafkaConsumer, KafkaProducer
import configuration


class MessageBrokerContainer(containers.DeclarativeContainer):
  config = providers.Configuration()
  config.from_dict(configuration.configuration)
  kafka_repository = providers.Singleton(KafkaRepository, bootstrap_servers=config.KAFKA_HOST)
  kafka_consumer = providers.Factory(KafkaConsumer, bootstrap_servers=config.KAFKA_HOST, group_id=config.KAFKA_GROUP_ID, auto_offset_reset=config.KAFKA_AUTO_OFFSET_RESET)
  kafka_producer = providers.Factory(KafkaProducer, bootstrap_servers=config.KAFKA_HOST)