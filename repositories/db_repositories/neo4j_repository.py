# app/repositories/db_repositories/neo4j_repository.py
from .base_repository import IDBRepository
from neo4j import GraphDatabase

class Neo4jRepository(IDBRepository):
    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def insert(self, table: str, data: dict):
        with self._driver.session() as session:
            query = self._generate_insert_query(table, data)
            session.write_transaction(lambda tx: tx.run(query, **data))

    def select(self, table: str, conditions: str):
        with self._driver.session() as session:
            query = f"MATCH (n:{table}) WHERE {conditions} RETURN n"
            result = session.read_transaction(lambda tx: tx.run(query))
            return [record['n'] for record in result]

    def remove_all_data(self):
        with self._driver.session() as session:
            session.write_transaction(lambda tx: tx.run("MATCH (n) DETACH DELETE n"))

    def _generate_insert_query(self, table: str, data: dict):
        keys = ', '.join(data.keys())
        params = ', '.join([f'${key}' for key in data.keys()])
        return f"CREATE (:{table} {{{keys}: {params}}})"