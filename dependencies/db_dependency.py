from repositories import CassandraRepository
from configuration import CASSANDRA_HOST, CASSANDRA_KEYSPACE
from containers import AppContainer

app_container = AppContainer()

def get_cassandra_repository() -> CassandraRepository:
    return app_container.database_container.cassandra_repository()