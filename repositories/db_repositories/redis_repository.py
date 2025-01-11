import redis
from .base_repository import IDBRepository

class RedisRepository(IDBRepository):
  def __init__(self, host: str, port: int, db: int):
    self.client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)

  def insert(self, table: str, data: dict):
    try:
      self.client.hmset(table, data)
    except Exception as e:
      raise Exception(f"Error inserting data into Redis: {str(e)}")

  def select(self, table: str, conditions: str):
    try:
        # For simplicity, assume conditions represent the field you want to retrieve.
        if conditions:  # Retrieve a specific field from the hash.
            return self.client.hget(table, conditions)
        else:  # Retrieve all fields from the hash.
            return self.client.hgetall(table)
    except Exception as e:
        raise Exception(f"Error fetching data from Redis: {str(e)}")

  def remove_all_data(self):
    self.client.flushdb()