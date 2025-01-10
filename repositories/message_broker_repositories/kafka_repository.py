from pprint import pprint
from repositories.message_broker_repositories import IMessageBrokerRepository
from kafka import KafkaProducer, KafkaConsumer
import json


class KafkaRepository(IMessageBrokerRepository):
    def __init__(self, bootstrap_servers: str):
        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self._consumers = []

    def publish(self, topic: str, message: dict):
        self._producer.send(topic, message)

    def subscribe(self, topic: str, callback):
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self._producer.config['bootstrap_servers'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        self._consumers.append(consumer)

        for message in consumer:
            callback(message.value)

    def close(self):
        self._producer.close()
        for consumer in self._consumers:
            consumer.close()