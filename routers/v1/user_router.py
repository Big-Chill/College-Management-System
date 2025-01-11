from fastapi import FastAPI, HTTPException, Depends, APIRouter, Response, Cookie, Request
from fastapi.responses import JSONResponse
from services.user_service import UserService
from configuration import CASSANDRA_KEYSPACE, CASSANDRA_HOST, REDIS_HOST, REDIS_PORT, SOLR_URL
from repositories import CassandraRepository, RedisRepository, SolrRepository

db_repository = CassandraRepository(contact_points=[CASSANDRA_HOST], keyspace=CASSANDRA_KEYSPACE)
cache_repository = RedisRepository(host=REDIS_HOST, port=REDIS_PORT, db=0)
search_repository = SolrRepository(solr_url=SOLR_URL)
user_service = UserService(db_repository=db_repository, cache_repository=cache_repository, search_repository=search_repository)

user_router = APIRouter()

@user_router.post("/sign_in")
async def sign_in(user: dict, request: Request):
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
async def sign_out(request: Request):
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

