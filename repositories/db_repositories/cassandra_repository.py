import os, sys
import cassandra
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy
from .base_repository import IDBRepository

class CassandraRepository(IDBRepository):
    def __init__(self, contact_points: list | str, keyspace: str):
        if isinstance(contact_points, str):
            contact_points = [contact_points]
        self.cluster = Cluster(contact_points, load_balancing_policy=DCAwareRoundRobinPolicy(local_dc='datacenter1'), protocol_version=5)
        self.session = self.cluster.connect(keyspace)
        self.keyspace = keyspace

    def insert(self, table: str, data: dict):
        keys = ', '.join(data.keys())
        values = ', '.join([f"'{str(value)}'" if isinstance(value, str) else str(value) for value in data.values()])
        query = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        self.session.execute(query)

    def bulk_insert(self, table: str, data: list):
        for row in data:
            self.insert(table, row)

    def select(self, table: str, conditions: str):
        query = f"SELECT * FROM {table}" + (f" WHERE {conditions}" if conditions else "")
        rows = self.session.execute(query)
        return self._convert_row_to_dict(rows)

    def remove_all_data(self):
        query = f"SELECT table_name FROM system_schema.tables WHERE keyspace_name='{self.keyspace}'"
        rows = self.session.execute(query)
        for row in rows:
            self.session.execute(f"TRUNCATE TABLE {row.table_name}")


    def _convert_row_to_dict(self, rows):
        if not rows:
            return []
        if isinstance(rows, cassandra.cluster.ResultSet):
            return [dict(row._asdict()) for row in rows]
        if isinstance(rows, list):
            return [dict(row._asdict()) if hasattr(row, '_asdict') else row for row in rows]
        elif hasattr(rows, '_asdict'):
            return [dict(rows._asdict())]
        return []
    
    def delete(self, table: str, conditions: str):
        query = f"DELETE FROM {table} WHERE {conditions}"
        self.session.execute(query)

    def close(self):
        self.cluster.shutdown()