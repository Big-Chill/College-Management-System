import os, sys, re
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .base_service import IService
from repositories import IDBRepository, CassandraRepository, RedisRepository, SolrRepository
from models import UserModel, UserByUserNameModel, SessionModel
from configuration import CASANDRA_KEYSPACE, CASSANDRA_HOST, REDIS_HOST, REDIS_PORT, SOLR_URL, JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from utlities import Jwt
from datetime import date

class UserService(IService):
    def __init__(self, db_repository: IDBRepository = None, cache_repository: IDBRepository = None, search_repository: IDBRepository = None):
            self.db_repository = db_repository
            self.cache_repository = cache_repository
            self.search_repository = search_repository

    def validate_data(self, data: dict, in_loop: bool = False):
        pass

    def sign_in(self, payload: dict):
            username = payload.get('username')
            password = payload.get('password')

            # Check if the user exists in the database
            user = self.db_repository.select(table='users_by_username', conditions=f"user_name='{username}'")
            if not user:
                return {"error": "User not found", "status": 404}
            user = user[0]

            # Check if the password matches
            if user.get('password') != password:
                return {"error": "Wrong password", "status": 400}

            APPROVED_SESSIONS = 2

            existing_sessions = self.db_repository.select(table='sessions', conditions=f"user_id='{user['user_id']}'")

            # Should not allow more than 1 active sessions
            if len(existing_sessions) >= APPROVED_SESSIONS:
                return {"error": f"User already has {APPROVED_SESSIONS} active sessions", "statusCode": 400}

            payload = {"user_id": user['user_id']}

            # Create a new session
            session = SessionModel(**payload)

            # Store the session in the database (Cassandra)
            self.db_repository.insert(table='sessions', data=session.dict())
            jwt_payload = {
                "username": username,
                "password": password,
                "user_id": user['user_id'],
                "session_id": session.session_id
            }

            # Create an access token for the user
            token = Jwt.create_access_token(data=jwt_payload)

            return {"token": token, "statusCode": 200}

    def sign_out(self, token: str):
        try:
            # Decode the token to get the user_id
            decoded_token = Jwt.verify_access_token(token)
            user_id = decoded_token.get('user_id')
            session_id = decoded_token.get('session_id')

            # Delete the session from the database
            self.db_repository.delete(table='sessions', conditions=f"user_id='{user_id}' AND session_id='{session_id}'")

            return {"message": "User logged out successfully", "statusCode": 200}
        except Exception as e:
            return {"error": str(e), "statusCode": 400}



