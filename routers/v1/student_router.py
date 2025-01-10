from fastapi import FastAPI, HTTPException, APIRouter, Request
from services.student_service import StudentService
from configuration import CASSANDRA_KEYSPACE, CASSANDRA_HOST, REDIS_HOST, REDIS_PORT, SOLR_URL
from repositories import CassandraRepository, RedisRepository, SolrRepository

db_repository = CassandraRepository(contact_points=[CASSANDRA_HOST], keyspace=CASSANDRA_KEYSPACE)
cache_repository = RedisRepository(host=REDIS_HOST, port=REDIS_PORT, db=0)
search_repository = SolrRepository(solr_url=SOLR_URL)
student_service = StudentService(db_repository=db_repository, cache_repository=cache_repository, search_repository=search_repository)

student_router = APIRouter()

@student_router.post("/create_student")
async def create_student(student: dict, request: Request):
    response = student_service.create_student(student)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}


@student_router.get("/get_all_students")
async def get_all_students(request: Request):
    response = student_service.get_all_students()
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student/{student_id}")
async def get_student(student_id: str, request: Request):
    response = student_service.get_student_by_id(student_id)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student_by_email/{email}")
async def get_student_by_email(email: str, request: Request):
    response = student_service.get_student_by_email(email)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student_by_phone/{phone}")
async def get_student_by_phone(phone: str, request: Request):
    response = student_service.get_student_by_phone_no(phone)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student_by_roll_no/{roll_no}")
async def get_student_by_roll_no(roll_no: str, request: Request):
    response = student_service.get_student_by_roll_no(roll_no)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student_by_course/{course}")
async def get_student_by_course(course: str, request: Request):
    response = student_service.get_student_by_course(course)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student_by_name/{name}")
async def get_student_by_name(name: str, request: Request):
    response = student_service.get_student_by_name(name)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/search_student_by_name/{name}")
async def search_student_by_name(name: str, request: Request):
    response = student_service.search_by_name(name)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/search_student_by_email/{email}")
async def search_student_by_email(email: str, request: Request):
    response = student_service.search_by_email(email)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}


@student_router.post("/add_bulk_students")
async def add_bulk_students(student_payload: dict, request: Request):
    students = student_payload.get("students", [])
    response = student_service.bulk_add_students(students)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.delete("/delete_all_students")
async def delete_all_students(request: Request):
    response = student_service.clear_all_data()
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}
