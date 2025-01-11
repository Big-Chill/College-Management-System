from containers import app_container
from services import CourseService


def get_course_service() -> CourseService:
    return app_container.service_container.course_service()