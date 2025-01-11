import json
from pprint import pprint
from confluent_kafka import Consumer
from typing import Optional
import logging

from repositories import Neo4jRepository, RedisRepository, MongoRepository
from .base_consumer import IBaseConsumer
from models import StudentModel, StudentByEmailModel, StudentByRollNoModel, StudentByPhoneNoModel, StudentByCourseModel, StudentByNameModel, StudentByUserModel

logger = logging.getLogger(__name__)

class StudentConsumer(IBaseConsumer):
    def __init__(
        self,
        consumer: Consumer,
        topic_name: str,
        neo4j_repository: Optional[Neo4jRepository] = None,
        redis_repository: Optional[RedisRepository] = None,
        mongo_repository: Optional[MongoRepository] = None
    ):
        self.consumer = consumer
        self.topic_name = topic_name
        self.neo4j_repository = neo4j_repository
        self.redis_repository = redis_repository
        self.mongo_repository = mongo_repository
        logger.info('Kafka Initialized')


    def consume(self):
        """Continuously consume messages from the Kafka topic."""
        try:
            self.consumer.subscribe([self.topic_name])
            print(f'-------------Subscribed to topic {self.topic_name}-----------------')

            while True:
                message = self.consumer.poll(1.0)
                if message is None:
                    continue
                if message.error():
                    print(f"Consumer error: {message.error()}")
                    continue

                # Process the consumed message
                consumed_message = message.value().decode("utf-8")
                message_data = json.loads(consumed_message)
                pprint(f'Message Data :- {message_data}')

                if message_data.get("event") == "STUDENT_CREATED":
                    self.insert_into_cache(message_data["data"])

        except Exception as e:
            print(f"Error consuming message: {str(e)}")
        finally:
            self.close()

    def insert_into_cache(self, event_data):
        try:
            key = event_data.get("key")
            value = event_data.get("value")
            method = event_data.get("method")

            if not key or not value or not method:
                return
            if method == "insert":
                self.redis_repository.insert(table=key, data=value)
            elif method == "sadd":
                self.redis_repository.client.sadd(key, value)
        except Exception as e:
            print(f"Error inserting student into cache: {str(e)}")


    def close(self):
        """Close the Kafka consumer."""
        self.consumer.close()