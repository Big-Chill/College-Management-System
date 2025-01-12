from fastapi import FastAPI, HTTPException, Depends, APIRouter, Request
from fastapi.responses import JSONResponse
from services.user_service import UserService
from dependencies import get_user_service

user_router = APIRouter()

@user_router.post("/sign_in")
async def sign_in(user: dict, request: Request, user_service: UserService = Depends(get_user_service)):
    cookies = request.cookies
    if cookies and "access-token" in cookies:
        raise HTTPException(status_code=400, detail={"error": "User is already logged in", "statusCode": 400})
    response = user_service.sign_in(user)
    token = response.get("token")
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})

    content = {
        "message": "User signed in successfully",
        "statusCode": status_code
    }
    response = JSONResponse(content=content)
    response.set_cookie(key="access-token", value=token, httponly=True)
    response.status_code = status_code
    return response

@user_router.post("/sign_out")
async def sign_out(request: Request,user_service: UserService = Depends(get_user_service)):
    user = request.state.user
    token = request.cookies.get("access-token")
    response = user_service.sign_out(token)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})

    content = {
        "message": "User signed out successfully",
        "statusCode": status_code
    }
    response = JSONResponse(content=content)
    response.delete_cookie(key="access-token")
    response.status_code = status_code
    return response

@user_router.get("/get_user_details/{user_id}")
async def get_user_details(user_id: str, user_service: UserService = Depends(get_user_service)):
    response = user_service.get_user_details(user_id)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})

    content = {
        "data": response.get("success"),
        "statusCode": status_code
    }
    return content

@user_router.get("/get_user_details_by_username/{username}")
async def get_user_details_by_username(username: str, user_service: UserService = Depends(get_user_service)):
    response = user_service.get_user_details_by_username(username)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})

    content = {
        "data": response.get("success"),
        "statusCode": status_code
    }
    return content

@user_router.post("/update_password")
async def update_password(payload: dict, user_service: UserService = Depends(get_user_service)):
    response = user_service.update_password(payload)
    status_code = response.get("statusCode", 200)
    if "error" in response:
        raise HTTPException(status_code=status_code, detail={"error": response.get("error"), "statusCode": status_code})

    content = {
        "message": "Password updated successfully",
        "statusCode": status_code
    }
    return content
