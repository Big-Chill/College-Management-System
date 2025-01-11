from containers import AppContainer
from services import CourseService, StudentService, UserService

app_container = AppContainer()

def get_course_service() -> CourseService:
    return app_container.service_container.course_service()

def get_student_service() -> StudentService:
    return app_container.service_container.student_service()

def get_user_service() -> UserService:
    return app_container.service_container.user_service()