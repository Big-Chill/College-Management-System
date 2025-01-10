import os, sys
from typing import List, Dict, Union
from pprint import pprint
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .base_service import IService
from configuration import CASSANDRA_KEYSPACE, CASSANDRA_HOST, REDIS_HOST, REDIS_PORT, SOLR_URL
from repositories import IDBRepository, IMessageBrokerRepository, CassandraRepository, RedisRepository, SolrRepository, KafkaRepository
from models import CourseModel, CourseDurationLookupModel, CourseByName, CourseByCredits


class CourseService(IService):
    def __init__(self, db_repository: IDBRepository = None, cache_repository: IDBRepository = None, search_repository: IDBRepository = None, message_broker_repository: IMessageBrokerRepository= None):
        self.db_repository = db_repository
        self.cache_repository = cache_repository
        self.search_repository = search_repository
        self.message_broker_repository = message_broker_repository

    def validate_data(self, data: dict):
        try:
            course_model = CourseModel(**data)
        except ValueError as e:
            raise ValueError(f"Error validating course data: {str(e)}")

        prepared_data = course_model.validate_and_prepare_data(data)
        return prepared_data, course_model

    def create_course(self, course: dict):
        try:
            prepared_data, course_model = self.validate_data(course)
        except ValueError as e:
            return {"error": str(e), "statusCode": 400}

        redis_repo = self.cache_repository

        if redis_repo.select(table=course_model.course_name, conditions=""):
            return {"error": "Course with the same name already exists", "statusCode": 400}

        try:
            self.db_repository.insert(table="courses", data=prepared_data)
            secondary_records = [
                {"table": "courses_duration_lookup", "data": CourseDurationLookupModel(course_duration=course_model.course_duration, course_duration_unit=course_model.course_duration_unit, course_id=course_model.id).dict()},
                {"table": "courses_by_name", "data": CourseByName(course_name=course_model.course_name, course_id=course_model.id, course_description=course_model.course_description).dict()},
                {"table": "courses_by_credits", "data": CourseByCredits(course_credits=course_model.course_credits, course_id=course_model.id, course_name=course_model.course_name, course_duration=course_model.course_duration, course_duration_unit=course_model.course_duration_unit).dict()}
            ]

            for record in secondary_records:
                self.db_repository.insert(table=record["table"], data=record["data"])
            message = {
                "event": "COURSE_CREATED",
                "data": course_model.dict()
            }
            self.message_broker_repository.publish(topic="course_events", message=message)
        except Exception as e:
            return {"error": f"Error inserting course: {str(e)}", "statusCode": 500}

        return {"success": course_model.dict(), "statusCode": 201}

    def bulk_add_course(self, courses: List):
        prepare_courses = []
        errors = []
        redis_repo = self.cache_repository

        for course in courses:
            try:
                prepared_data, course_model = self.validate_data(course)
                existing_course = redis_repo.select(table=course_model.course_name, conditions="")
                if existing_course:
                    errors.append({
                        "course": course,
                        "error": "Course with the same name already exists"
                    })
                    continue
                prepare_courses.append(prepared_data)
            except ValueError as e:
                errors.append({
                    "course": course,
                    "error": str(e)
                })

        if errors:
            return {"error": errors, "statusCode": 400}

        try:
            self.db_repository.bulk_insert(table="courses", data=prepare_courses)
            secondary_data = {
                "courses_duration_lookup": [],
                "courses_by_name": [],
                "courses_by_credits": []
            }
            # redis_pipeline = redis_repo.client.pipeline()
            for course in prepare_courses:
                course_id = course["id"]
                secondary_data["courses_duration_lookup"].append(CourseDurationLookupModel(course_duration=course["course_duration"], course_duration_unit=course["course_duration_unit"], course_id=course_id).dict())
                secondary_data["courses_by_name"].append(CourseByName(course_name=course["course_name"], course_id=course_id, course_description=course["course_description"]).dict())
                secondary_data["courses_by_credits"].append(CourseByCredits(course_credits=course["course_credits"], course_id=course_id, course_name=course["course_name"], course_duration=course["course_duration"], course_duration_unit=course["course_duration_unit"]).dict())
                message = {
                    "event": "COURSE_CREATED",
                    "data": course
                }
                self.message_broker_repository.publish(topic="course_events", message=message)


            for table, data in secondary_data.items():
                self.db_repository.bulk_insert(table=table, data=data)
        except Exception as e:
            return {"error": f"Error inserting courses: {str(e)}", "statusCode": 500}

        return {"success": prepare_courses, "statusCode": 201}

    def get_courses_by_duration(self, duration: int, duration_unit: str):
        redis_repo = self.cache_repository
        course_ids = redis_repo.client.smembers(f"course:{duration}:{duration_unit}")

        if not course_ids:
            course_ids = self.db_repository.select(table="courses_duration_lookup", conditions=f"course_duration={duration} AND course_duration_unit='{duration_unit}'")
            if not course_ids:
                return {"error": "No courses found", "statusCode": 404}

        courses = []
        for course_id in course_ids:
            query = f"id='{course_id}'"
            course = self.db_repository.select(table="courses", conditions=query)
            if not course:
                continue
            courses.extend(course)

        if not courses:
            return {"error": "No courses found", "statusCode": 404}

        return {"success": courses, "statusCode": 200}

    def get_courses_by_credits(self, credits: int):
        db_repo = self.db_repository

        courses_lookup = db_repo.select(table="courses_by_credits", conditions=f"course_credits={credits}")
        if not courses_lookup:
            return {"error": "No courses found", "statusCode": 404}

        courses = []
        for course in courses_lookup:
            course_id = course.get("course_id")
            if not course_id:
                continue
            query = f"id='{course_id}'"
            course = db_repo.select(table="courses", conditions=query)
            if not course:
                continue
            courses.extend(course)

        if not courses:
            return {"error": "No courses found", "statusCode": 404}

        return {"success": courses, "statusCode": 200}
