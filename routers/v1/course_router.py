from fastapi import FastAPI, HTTPException, APIRouter, Request
from services.course_service import CourseService
from configuration import CASANDRA_KEYSPACE, CASSANDRA_HOST, REDIS_HOST, REDIS_PORT, SOLR_URL, KAFKA_HOST
from repositories import CassandraRepository, RedisRepository, KafkaRepository


db_repository = CassandraRepository(contact_points=[CASSANDRA_HOST], keyspace=CASANDRA_KEYSPACE)
cache_repository = RedisRepository(host=REDIS_HOST, port=REDIS_PORT, db=0)
course_service = CourseService(db_repository=db_repository, cache_repository=cache_repository, message_broker_repository=KafkaRepository(bootstrap_servers=KAFKA_HOST))

course_router = APIRouter()

@course_router.post("/create_course")
async def create_course(course: dict, request: Request):
    response = course_service.create_course(course)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@course_router.get("/get_course_by_duration/{course_duration}/{course_duration_unit}")
async def get_course_by_duration(course_duration: int, course_duration_unit: str, request: Request):
    response = course_service.get_courses_by_duration(course_duration, course_duration_unit)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@course_router.get("/get_course_by_credits/{course_credits}")
async def get_course_by_credits(course_credits: int, request: Request):
    response = course_service.get_courses_by_credits(course_credits)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}


@course_router.post("/add_bulk_courses")
async def add_bulk_courses(course_payload: dict, request: Request):
    courses = course_payload.get("courses", [])
    response = course_service.bulk_add_course(courses)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}