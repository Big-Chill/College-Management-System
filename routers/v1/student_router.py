from fastapi import FastAPI, HTTPException, APIRouter, Request, Depends
from services.student_service import StudentService
from containers import AppContainer
from dependencies import get_student_service

app_container = AppContainer()
student_router = APIRouter()

@student_router.post("/create_student")
async def create_student(student: dict, request: Request, student_service: StudentService = Depends(get_student_service)):
    response = student_service.create_student(student)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}


@student_router.get("/get_all_students")
async def get_all_students(request: Request, student_service: StudentService = Depends(get_student_service)):
    response = student_service.get_all_students()
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student/{student_id}")
async def get_student(student_id: str, request: Request, student_service: StudentService = Depends(get_student_service)):
    response = student_service.get_student_by_id(student_id)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student_by_email/{email}")
async def get_student_by_email(email: str, request: Request, student_service: StudentService = Depends(get_student_service)):
    response = student_service.get_student_by_email(email)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student_by_phone/{phone}")
async def get_student_by_phone(phone: str, request: Request, student_service: StudentService = Depends(get_student_service)):
    response = student_service.get_student_by_phone_no(phone)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student_by_roll_no/{roll_no}")
async def get_student_by_roll_no(roll_no: str, request: Request, student_service: StudentService = Depends(get_student_service)):
    response = student_service.get_student_by_roll_no(roll_no)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student_by_course/{course}")
async def get_student_by_course(course: str, request: Request, student_service: StudentService = Depends(get_student_service)):
    response = student_service.get_student_by_course(course)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/get_student_by_name/{name}")
async def get_student_by_name(name: str, request: Request, student_service: StudentService = Depends(get_student_service)):
    response = student_service.get_student_by_name(name)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/search_student_by_name/{name}")
async def search_student_by_name(name: str, request: Request, student_service: StudentService = Depends(get_student_service)):
    response = student_service.search_by_name(name)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.get("/search_student_by_email/{email}")
async def search_student_by_email(email: str, request: Request, student_service: StudentService = Depends(get_student_service)):
    response = student_service.search_by_email(email)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}


@student_router.post("/add_bulk_students")
async def add_bulk_students(student_payload: dict, request: Request, student_service: StudentService = Depends(get_student_service)):
    students = student_payload.get("students", [])
    response = student_service.bulk_add_students(students)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}

@student_router.delete("/delete_all_students")
async def delete_all_students(request: Request, student_service: StudentService = Depends(get_student_service)):
    response = student_service.clear_all_data()
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})
    return {"data": response.get("success"), "statusCode": status_code}
