from repositories import CassandraRepository
from configuration import CASSANDRA_HOST, CASANDRA_KEYSPACE

def get_db_repository() -> CassandraRepository:
    return CassandraRepository(
        contact_points=[CASSANDRA_HOST],
        keyspace=CASANDRA_KEYSPACE
    )
