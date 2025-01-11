from containers import AppContainer
from repositories import CassandraRepository, RedisRepository, SolrRepository, Neo4jRepository, MongoRepository

app_container = AppContainer()

def get_cassandra_repository() -> CassandraRepository:
    return app_container.database_container.cassandra_repository()

def get_redis_repository() -> RedisRepository:
    return app_container.database_container.redis_repository()

def get_solr_repository() -> SolrRepository:
    return app_container.database_container.solr_repository()

def get_neo4j_repository() -> Neo4jRepository:
    return app_container.database_container.neo4j_repository()

def get_mongo_repository() -> MongoRepository:
    return app_container.database_container.mongo_repository()

