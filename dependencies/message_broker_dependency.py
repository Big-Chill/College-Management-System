from containers import AppContainer
from repositories import KafkaRepository

app_container = AppContainer()

def get_kafka_repository() -> KafkaRepository:
    return app_container.message_broker_container.kafka_repository()