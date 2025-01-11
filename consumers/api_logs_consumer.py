import json
from confluent_kafka import Consumer
from typing import Optional
import logging

from repositories import RedisRepository, Neo4jRepository, MongoRepository, CassandraRepository, SolrRepository
from .base_consumer import IBaseConsumer

logger = logging.getLogger(__name__)

class ApiLogsConsumer(IBaseConsumer):
    def __init__(
            self,
            consumer: Consumer,
            topic_name: str,
            neo4j_repository: Optional[Neo4jRepository] = None,
            redis_repository: Optional[RedisRepository] = None,
            mongo_repository: Optional[MongoRepository] = None,
            cassandra_repository: Optional[CassandraRepository] = None,
            solr_repository: Optional[SolrRepository] = None
        ):
            self.consumer = consumer
            self.topic_name = topic_name
            self.neo4j_repository = neo4j_repository
            self.redis_repository = redis_repository
            self.mongo_repository = mongo_repository
            self.cassandra_repository = cassandra_repository
            self.solr_repository = solr_repository
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

                    if message_data.get("event") == "API_LOG_CREATED":
                        self.insert_into_mongo(message_data["data"])
                        print(f'Logged request: {message_data["data"]}')
            except Exception as e:
                print(f"Error consuming message: {str(e)}")
            finally:
                self.close()

    def insert_into_mongo(self, log_data):
            try:
                self.mongo_repository.insert("api_logs", log_data)
            except Exception as e:
                print(f"Error saving log data: {e}")

    def close(self):
            """Cleans up any open kafka consumers"""
            self.consumer.close()
            logger.info('Kafka Closed')

