from dependency_injector import containers, providers
from repositories import MongoRepository, CassandraRepository, RedisRepository, SolrRepository, Neo4jRepository
import configuration

class DatabaseContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_dict(configuration.configuration)
    mongo_repository = providers.Singleton(MongoRepository, mongo_uri=config.MONGO_HOST, mongo_db=config.MONGO_DB)
    cassandra_repository = providers.Singleton(CassandraRepository, contact_points=[config.CASSANDRA_HOST], keyspace=config.CASSANDRA_KEYSPACE)
    redis_repository = providers.Singleton(RedisRepository, host=config.REDIS_HOST, port=config.REDIS_PORT, db=0)
    solr_repository = providers.Singleton(SolrRepository, solr_url=config.SOLR_URL)
    neo4j_repository = providers.Singleton(Neo4jRepository, uri=config.NEO4J_HOST, user=config.NEO4J_USER, password=config.NEO4J_PASSWORD)