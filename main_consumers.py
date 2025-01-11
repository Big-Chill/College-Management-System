import threading
import logging
from confluent_kafka import Consumer
from consumers import CourseConsumer, ApiLogsConsumer
from repositories import Neo4jRepository, RedisRepository, MongoRepository
from configuration import NEO4J_HOST, NEO4J_USER, NEO4J_PASSWORD, REDIS_HOST, REDIS_PORT, MONGO_DB, MONGO_HOST, KAFKA_HOST

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka and repository configurations
kafka_config = {
    "bootstrap.servers": KAFKA_HOST,
    "group.id": "my-consumer-group",
    "auto.offset.reset": "earliest",
}

neo4j_config = {
    "uri": NEO4J_HOST,
    "user": NEO4J_USER,
    "password": NEO4J_PASSWORD,
}

redis_config = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
}

mongo_config = {
    "host": MONGO_HOST,
    "db": MONGO_DB,
}


def start_consumer(consumer_class, kafka_config, topic_name, neo4j_repository, redis_repository, mongo_repository):
    """
    Starts a consumer instance and runs its `consume` method in a try-except block.
    """
    consumer = consumer_class(
        consumer=Consumer(kafka_config),
        topic_name=topic_name,
        neo4j_repository=neo4j_repository,
        redis_repository=redis_repository,
        mongo_repository=mongo_repository,
    )
    try:
        logger.info(f"Starting {consumer_class.__name__} for topic: {topic_name}")
        consumer.consume()
    except KeyboardInterrupt:
        logger.info(f"{consumer_class.__name__} stopped by user.")
    except Exception as e:
        logger.error(f"Error in {consumer_class.__name__}: {e}")
    finally:
        consumer.close()


def initialize_consumers():
    """
    Initializes and starts consumers in separate threads. Can be called from another script.
    """
    consumers = [
        {"class": CourseConsumer, "topic": "course_events"},
        {"class": ApiLogsConsumer, "topic": "api_events"},
    ]

    # Initialize repository instances
    neo4j_repository = Neo4jRepository(
        uri=neo4j_config["uri"],
        user=neo4j_config["user"],
        password=neo4j_config["password"],
    )

    redis_repository = RedisRepository(
        host=redis_config["host"],
        port=redis_config["port"],
        db=0,
    )

    mongo_repository = MongoRepository(
        mongo_uri=mongo_config["host"],
        mongo_db=mongo_config["db"],
    )

    # Start each consumer in a separate thread
    threads = []
    for consumer_info in consumers:
        thread = threading.Thread(
            target=start_consumer,
            args=(
                consumer_info["class"],
                kafka_config,
                consumer_info["topic"],
                neo4j_repository,
                redis_repository,
                mongo_repository,
            ),
            daemon=True,
        )
        threads.append(thread)
        thread.start()

    return threads
