import json
from pprint import pprint
from confluent_kafka import Consumer
from typing import Optional
import logging

from repositories import Neo4jRepository, RedisRepository, MongoRepository, CassandraRepository, SolrRepository
from .base_consumer import IBaseConsumer
from models import StudentModel, UserModel, UserByUserNameModel

logger = logging.getLogger(__name__)

class StudentConsumer(IBaseConsumer):
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
                pprint(f'Message Data :- {message_data}')

                if message_data.get("event") == "STUDENT_CREATED":
                    self.insert_into_cache(message_data["data"])
                elif message_data.get("event") == "STUDENT_SIGNED_UP":
                    self.sign_up_student(message_data["data"])
                elif message_data.get("event") == "STUDENT_INDEXED":
                    self.insert_into_solr(message_data["data"])

        except Exception as e:
            print(f"Error consuming message: {str(e)}")
        finally:
            self.close()

    def insert_into_solr(self, event_data):
        try:
            table = event_data.get("table")
            data = event_data.get("data")
            student_model = StudentModel(**data)
            self.solr_repository.insert(table=table, data=student_model.dict())
        except Exception as e:
            print(f"Error indexing student in Solr: {str(e)}")

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

    def sign_up_student(self, student: dict):
        try:
            student_model = StudentModel(**student)
            user_payload = {
                "user_name": student_model.roll_no,
                "password": student_model.roll_no,
                "email": student_model.email,
                "reference_id": student_model.id
            }
            user_model = UserModel(**user_payload)
            self.cassandra_repository.insert(table="users", data=user_model.dict())
            self.cassandra_repository.insert(table="users_by_username", data=UserByUserNameModel(user_name=user_model.user_name, user_id=user_model.id, reference_id=user_model.reference_id, password=user_model.password).dict())
        except Exception as e:
            print(f"Error signing up student: {str(e)}")
    def close(self):
        """Close the Kafka consumer."""
        self.consumer.close()