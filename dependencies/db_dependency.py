from repositories import CassandraRepository
from configuration import CASSANDRA_HOST, CASSANDRA_KEYSPACE

def get_db_repository() -> CassandraRepository:
    return CassandraRepository(
        contact_points=[CASSANDRA_HOST],
        keyspace=CASSANDRA_KEYSPACE
    )
