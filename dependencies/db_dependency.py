from repositories import CassandraRepository
from configuration import CASSANDRA_HOST, CASSANDRA_KEYSPACE
from containers import app_container


def get_cassandra_repository() -> CassandraRepository:
    return app_container.database_container.cassandra_repository()