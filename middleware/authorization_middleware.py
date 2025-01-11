import re
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED
from utlities import Jwt
from configuration import INTERNAL_TOKEN
from dependencies import get_db_repository

class AuthorizationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.db_repository = get_db_repository()

    async def dispatch(self, request: Request, call_next):
        TOKEN_MSG = "Missing Authorization Token! Unauthorized to access this resource"
        URLS_TO_SKIP = ["/v1/user/sign_in"]
        for url in URLS_TO_SKIP:
            if re.match(url, request.url.path):
                response = await call_next(request)
                return response

        token = request.cookies.get("access-token")
        if not token:
            token = request.headers.get("Authorization")
            if not token or (token and token != INTERNAL_TOKEN):
                return JSONResponse(
                    status_code=HTTP_401_UNAUTHORIZED,
                    content={"message": TOKEN_MSG}
                )

        if token == INTERNAL_TOKEN:
            response = await call_next(request)
            return response

        try:
            payload = Jwt.verify_access_token(token)
            user_id = payload.get('user_id')
            session_id = payload.get('session_id')
            query = f"user_id='{user_id}' and session_id='{session_id}'"
            existing_sessions = self.db_repository.select(table='sessions', conditions=query)
            if not existing_sessions:
                return JSONResponse(
                    status_code=HTTP_401_UNAUTHORIZED,
                    content={"message": TOKEN_MSG}
                )
            request.state.user = payload
        except HTTPException as e:
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"message": TOKEN_MSG}
            )

        response = await call_next(request)
        return response
