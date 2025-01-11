from fastapi import FastAPI, HTTPException, APIRouter, Request, Depends
from services.course_service import CourseService
from containers import AppContainer

app_container = AppContainer()

def get_course_service() -> CourseService:
    return app_container.service_container.course_service()

course_router = APIRouter()

@course_router.post("/create_course")
async def create_course(course: dict, request: Request, course_service: CourseService = Depends(get_course_service)):
    response = course_service.create_course(course)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@course_router.get("/get_course_by_duration/{course_duration}/{course_duration_unit}")
async def get_course_by_duration(course_duration: int, course_duration_unit: str, request: Request, course_service: CourseService = Depends(get_course_service)):
    response = course_service.get_courses_by_duration(course_duration, course_duration_unit)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

# /get_course_by_credits endpoint
@course_router.get("/get_course_by_credits/{course_credits}")
async def get_course_by_credits(course_credits: int, request: Request, course_service: CourseService = Depends(get_course_service)):
    response = course_service.get_courses_by_credits(course_credits)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

# /add_bulk_courses endpoint
@course_router.post("/add_bulk_courses")
async def add_bulk_courses(course_payload: dict, request: Request, course_service: CourseService = Depends(get_course_service)):
    courses = course_payload.get("courses", [])
    response = course_service.bulk_add_course(courses)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}