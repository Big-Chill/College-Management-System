import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from dependencies import get_kafka_repository

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.message_broker_repository = get_kafka_repository()

    async def dispatch(self, request: Request, call_next):
        body = await request.body()

        # Log request data
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "path_params": dict(request.path_params),
            "headers": dict(request.headers),
            "body": json.loads(body.decode("utf-8")) if body else None,
            "ip": request.client.host,
            "timestamp": datetime.now().isoformat()
        }

        message = {
            "event": "API_LOG_CREATED",
            "data": log_data
        }

        self.message_broker_repository.publish(topic="api_events", message=message)

        async def receive():
            return {"type": "http.request", "body": body}
        request._receive = receive

        # Process the request
        response = await call_next(request)

        return response