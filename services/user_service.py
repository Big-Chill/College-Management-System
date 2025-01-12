import os, sys, re
from .base_service import IService
from repositories import IDBRepository
from models import SessionModel
from utlities import Jwt

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

    def get_user_details(self, user_id):
        try:
            user = self.db_repository.select(table='users', conditions=f"id='{user_id}'")
            if not user:
                return {"error": "User not found", "statusCode": 404}
            user = user[0]
            reference_id = user.get('reference_id')
            if 'student' in reference_id:
                student = self.db_repository.select(table='students', conditions=f"id='{reference_id}'")
                if not student:
                    return {"error": "Student not found", "statusCode": 404}
                respone_payload = {
                    **user,
                    **student[0]
                }
                return {"success": respone_payload, "statusCode": 200}
            return {"success": user[0], "statusCode": 200}
        except Exception as e:
            return {"error": str(e), "statusCode": 400}

    def get_user_details_by_username(self, username):
        try:
            user = self.db_repository.select(table='users_by_username', conditions=f"user_name='{username}'")
            if not user:
                return {"error": "User not found", "statusCode": 404}
            user = user[0]
            reference_id = user.get('reference_id')

            if 'student' in reference_id:
                student = self.db_repository.select(table='students', conditions=f"id='{reference_id}'")
                if not student:
                    return {"error": "Student not found", "statusCode": 404}
                respone_payload = {
                    **user,
                    **student[0]
                }
                return {"success": respone_payload, "statusCode": 200}
            return {"success": user[0], "statusCode": 200}
        except Exception as e:
            return {"error": str(e), "statusCode": 400}

    def update_password(self, payload: dict):
        try:
            username = payload.get('username')
            old_password = payload.get('old_password')
            new_password = payload.get('new_password')

            user = self.db_repository.select(table='users_by_username', conditions=f"user_name='{username}'")
            if not user:
                return {"error": "User not found", "statusCode": 404}
            user = user[0]

            if user.get('password') != old_password:
                return {"error": "Old password is incorrect", "statusCode": 400}

            user_id = user.get('user_id')

            self.db_repository.update(table='users_by_username', data={"password": new_password}, conditions=f"user_name='{username}' and user_id='{user['user_id']}' and reference_id='{user['reference_id']}'")
            self.db_repository.update(table='users', data={"password": new_password}, conditions=f"id='{user_id}' and reference_id='{user['reference_id']}' and user_name='{username}'")
            return {"message": "Password updated successfully", "statusCode": 200}
        except Exception as e:
            return {"error": str(e), "statusCode": 400}



