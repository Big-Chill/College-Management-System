import json
from pprint import pprint
from confluent_kafka import Consumer
from typing import Optional
import logging

from repositories import Neo4jRepository, RedisRepository, MongoRepository, CassandraRepository, SolrRepository
from .base_consumer import IBaseConsumer
from models import CourseModel, CourseDurationLookupModel, CourseByName, CourseByCredits

logger = logging.getLogger(__name__)

class CourseConsumer(IBaseConsumer):
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

                if message_data.get("event") == "COURSE_CREATED":
                    self.insert_into_cache(message_data["data"])
                elif message_data.get("event") == "COURSE_LOOKUP_CREATED":
                    self.insert_lookup_data(message_data["data"])

        except Exception as e:
            print(f"Error consuming message: {str(e)}")
        finally:
            self.close()

    def insert_lookup_data(self, event_data):
        try:
            table = event_data.get("table")
            data = event_data.get("data")
            self.cassandra_repository.insert(table=table, data=data)
        except Exception as e:
            print(f"Error inserting lookup data into cache: {str(e)}")
        finally:
            return

    def insert_into_cache(self, course_data):
        try:
            course_model = CourseModel(**course_data)
            self.redis_repository.insert(table=course_model.course_name, data=course_model.dict())
            self.redis_repository.client.sadd(f"course:{course_model.course_duration}:{course_model.course_duration_unit}", course_model.id)
            self.redis_repository.client.sadd(f"course:{course_model.course_credits}", course_model.id)
            self.redis_repository.insert(table=course_model.course_name, data=CourseByName(course_name=course_model.course_name, course_id=course_model.id, course_description=course_model.course_description).dict())
        except Exception as e:
            print(f"Error inserting course into cache: {str(e)}")
        finally:
            return


    def close(self):
        """Close the Kafka consumer and Neo4j connection."""
        print("Closing consumer and Neo4j repository...")
        self.consumer.close()

