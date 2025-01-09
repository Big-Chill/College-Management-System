import os
from dotenv import load_dotenv
env = os.getenv('ENV', 'development')

if env == 'development':
    load_dotenv('.env.local')
else:
    load_dotenv('.env.prod')


CASSANDRA_HOST = os.getenv('CASSANDRA_HOST')
CASANDRA_KEYSPACE = os.getenv('CASANDRA_KEYSPACE')
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
SOLR_URL = os.getenv('SOLR_URL')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
INTERNAL_TOKEN = os.getenv('INTERNAL_TOKEN')
NEO4J_HOST = os.getenv('NEO4J_HOST')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
KAFKA_HOST = os.getenv('KAFKA_HOST')
MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_DB = os.getenv('MONGO_DB')



