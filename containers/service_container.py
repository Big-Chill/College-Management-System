from dependency_injector import containers, providers
from repositories import CassandraRepository, RedisRepository, KafkaRepository
from services import CourseService, StudentService
import configuration

class ServiceContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_dict(configuration.configuration)
    cassandra_repository = providers.Singleton(CassandraRepository, contact_points=config.CASSANDRA_CONTACT_POINTS, keyspace=config.CASSANDRA_KEYSPACE)
    redis_repository = providers.Singleton(RedisRepository, host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
    kafka_repository = providers.Singleton(KafkaRepository, bootstrap_servers=config.KAFKA_HOST)
    course_service = providers.Factory(CourseService, db_repository=cassandra_repository, cache_repository=redis_repository, search_repository=cassandra_repository, message_broker_repository=kafka_repository)
    student_service = providers.Factory(StudentService, db_repository=cassandra_repository, cache_repository=redis_repository, search_repository=cassandra_repository)