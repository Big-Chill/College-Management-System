import os
from fastapi import FastAPI
from routers.v1 import student_router, user_router, course_router
from middleware import AuthorizationMiddleware, LoggingMiddleware
from containers import AppContainer
from main_consumers import initialize_consumers

container = AppContainer()

kafka_repository = container.message_broker_container.kafka_repository
cassandra_repository = container.database_container.cassandra_repository

# Retrieve settings from environment variables
APP_TITLE = os.getenv("APP_TITLE", "College Management System")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "This is a simple College Management System")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

# Create FastAPI instance
app = FastAPI(title=APP_TITLE, description=APP_DESCRIPTION, version=APP_VERSION)

# Add middleware
app.add_middleware(LoggingMiddleware, message_broker_repository=kafka_repository)
app.add_middleware(AuthorizationMiddleware, db_repository=cassandra_repository)

# Include routers
app.include_router(student_router, prefix="/v1/student", tags=["Student"])
app.include_router(user_router, prefix="/v1/user", tags=["User"])
app.include_router(course_router, prefix="/v1/course", tags=["Course"])

# Start consumers during app startup
consumer_threads = []

@app.on_event("startup")
async def startup_event():
    global consumer_threads
    consumer_threads = initialize_consumers()  # Start the consumer threads

@app.on_event("shutdown")
async def shutdown_event():
    # Clean up consumer threads if necessary
    for thread in consumer_threads:
        if thread.is_alive():
            print(f"Stopping thread: {thread.name}")
