import os, sys, re
from typing import List, Dict, Union
from pprint import pprint
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .base_service import IService
from repositories import IDBRepository, CassandraRepository, RedisRepository, SolrRepository, IMessageBrokerRepository
from models import StudentModel, StudentByEmailModel, StudentByRollNoModel, StudentByPhoneNoModel, StudentByCourseModel, StudentByNameModel, UserModel, UserByUserNameModel
from configuration import CASSANDRA_HOST, REDIS_HOST, REDIS_PORT, SOLR_URL


class StudentService(IService):
    def __init__(self, db_repository: IDBRepository = None, cache_repository: IDBRepository = None, search_repository: IDBRepository = None, message_broker_repository: IMessageBrokerRepository= None):
        self.db_repository = db_repository
        self.cache_repository = cache_repository
        self.search_repository = search_repository
        self.message_broker_repository = message_broker_repository

    def auto_generate_roll_no_single(self, data: dict):
        _prefix = f"{str(data['enrollment_year'])[-2:]}{str(data['enrollment_month']).zfill(2)}"
        _suffix = self.db_repository.select(table="students", conditions="")
        if not _suffix:
            return f"{_prefix}001"
        _suffix = _suffix[-1]["roll_no"]
        _counter = int(re.search(r"\d{3}$", _suffix).group()) + 1
        return f"{_prefix}{str(_counter).zfill(3)}"

    def auto_generate_roll_no_bulk(self, data: List[dict]):
        base_suffix = self.db_repository.select(table="students", conditions="")
        if not base_suffix:
            base_suffix = int("001")
        else:
            base_suffix = base_suffix[-1]["roll_no"]
            base_suffix = int(re.search(r"\d{3}$", base_suffix).group())
        for index, student in enumerate(data):
            _prefix = f"{str(student['enrollment_year'])[-2:]}{str(student['enrollment_month']).zfill(2)}"
            # Handle case for "001"
            _counter = base_suffix + index + 1 if base_suffix > 1 else base_suffix + index
            roll_no = f"{_prefix}{str(_counter).zfill(3)}"
            data[index]["roll_no"] = roll_no
        return data

    def sign_up_student(self, student: dict):
        message = {
            "event": "STUDENT_SIGNED_UP",
            "data": student
        }
        self.message_broker_repository.publish(topic="student_events", message=message)

    def bulk_sign_up_students(self, students: List[Dict[str, Union[str, int]]]):
        try:
            for student in students:
                message = {
                    "event": "STUDENT_SIGNED_UP",
                    "data": student
                }
                self.message_broker_repository.publish(topic="student_events", message=message)
            return {"success": "Students signed up successfully", "statusCode": 201}
        except Exception as e:
            return {"error": "Error signing up students in the system", "statusCode": 500}

    def validate_data(self, data: dict, in_loop: bool = False):
        try:
            if not in_loop:
                data["roll_no"] = self.auto_generate_roll_no_single(data)
            student_model = StudentModel(**data)
        except ValueError as e:
            raise ValueError(f"Error validating student data: {str(e)}")

        prepared_data = student_model.validate_and_prepare_data(data)
        return prepared_data, student_model

    def index_student_in_solr(self, student: dict):
        try:
            student_model = StudentModel(**student)
            self.search_repository.insert(table="students", data=student_model.dict())
        except Exception as e:
            return {"error": f"Error indexing student in Solr: {str(e)}", "statusCode": 500}
        return {"success": student_model.dict(), "statusCode": 201}

    def create_student(self, student: dict):
        try:
            # Validate input data
            prepared_data, student_model = self.validate_data(student)
        except ValueError as e:
            return {"error": str(e), "statusCode": 400}

        redis_repo = self.cache_repository

        # Check if the student already exists (by email) in Redis
        if redis_repo.select(table=student_model.email, conditions=""):
            return {"error": "Student with the same email already exists", "statusCode": 400}

        # Begin data insertion
        try:
            # Insert student data into the primary table
            self.db_repository.insert(table="students", data=student_model.dict())

            # Generate secondary table data
            secondary_records = [
                {"table": "students_by_roll_no", "data": StudentByRollNoModel(roll_no=student_model.roll_no, student_id=student_model.id).dict()},
                {"table": "students_by_email", "data": StudentByEmailModel(email=student_model.email, student_id=student_model.id).dict()},
                {"table": "students_by_phone_no", "data": StudentByPhoneNoModel(phone_no=student_model.phone_no, student_id=student_model.id).dict()},
                {"table": "students_by_course", "data": StudentByCourseModel(
                    course_id=student_model.course_id,
                    student_id=student_model.id,
                    name=student_model.name,
                    roll_no=student_model.roll_no,
                    email=student_model.email,
                    phone_no=student_model.phone_no
                ).dict()},
                {"table": "students_by_name", "data": StudentByNameModel(
                    name=student_model.name,
                    student_id=student_model.id,
                    roll_no=student_model.roll_no,
                    email=student_model.email,
                    phone_no=student_model.phone_no
                ).dict()},
            ]

            for record in secondary_records:
                self.db_repository.insert(table=record["table"], data=record["data"])

            # Cache the student data in Redis under different keys
            redis_keys = [
                student_model.id,                   # Cache by student_id
                student_model.email,                # Cache by email
                student_model.phone_no,            # Cache by phone number
                student_model.roll_no,             # Cache by roll number
            ]

            # Insert student data into Redis for each key
            for key in redis_keys:
                message = {
                    "event": "STUDENT_CREATED",
                    "data": {
                        "key": key,
                        "value": student_model.dict(),
                        "method": "insert"
                    }
                }
                self.message_broker_repository.publish(topic="student_events", message=message)
            # Cache by course_id using a Redis Set (to avoid overwriting)
            message = {
                "event": "STUDENT_CREATED",
                "data": {
                    "key": f"course:{student_model.course_id}",
                    "value": student_model.id,
                    "method": "sadd"
                }
            }
            self.message_broker_repository.publish(topic="student_events", message=message)

            # Add student to Solr index
            self.index_student_in_solr(student_model.dict())
            # Sign up student in the system
            self.sign_up_student(student_model.dict())

        except Exception as e:
            return {"error": f"Error inserting student: {str(e)}", "statusCode": 500}

        return {"success": student_model.dict(), "statusCode": 201}

    def bulk_add_students(self, students: List[Dict[str, Union[str, int]]]):
        """
        Bulk adds students to the database and caches their data in Redis.
        Handles validation, Cassandra inserts, and Redis caching.
        """
        prepared_students = []
        errors = []
        redis_repo = self.cache_repository

        students = self.auto_generate_roll_no_bulk(students)
        # Validate and prepare data
        for student in students:
            try:
                prepared_data, student_model = self.validate_data(student, in_loop=True)
                # Check for existing students in Redis
                existing_student = redis_repo.select(table=student_model.email, conditions="")
                if existing_student:
                    errors.append({
                        "student": student,
                        "error": "Student with the same email already exists"
                    })
                    continue
                prepared_students.append(student_model.dict())
            except ValueError as e:
                errors.append({"student": student, "error": str(e)})

        # If there are errors, return them and stop processing
        if errors:
            return {"error": errors, "statusCode": 400}

        try:
            # Batch insert into Cassandra main table
            self.db_repository.bulk_insert(table="students", data=prepared_students)

            # Prepare and batch insert secondary records
            secondary_data = {
                "students_by_roll_no": [],
                "students_by_email": [],
                "students_by_phone_no": [],
                "students_by_course": [],  # For course_id-based lookup
                "students_by_name": []  # For name-based lookup
            }

            for student in prepared_students:
                student_id = student['id']

                # Cassandra secondary tables
                secondary_data["students_by_roll_no"].append(
                    StudentByRollNoModel(roll_no=student['roll_no'], student_id=student_id).dict()
                )
                secondary_data["students_by_email"].append(
                    StudentByEmailModel(email=student['email'], student_id=student_id).dict()
                )
                secondary_data["students_by_phone_no"].append(
                    StudentByPhoneNoModel(phone_no=student['phone_no'], student_id=student_id).dict()
                )
                # For course-based lookup, multiple students can have the same course_id
                secondary_data["students_by_course"].append(
                    StudentByCourseModel(
                        course_id=student['course_id'],
                        student_id=student_id,
                        name=student['name'],
                        roll_no=student['roll_no'],
                        email=student['email'],
                        phone_no=student['phone_no']
                    ).dict()
                )

                # For name-based lookup
                secondary_data["students_by_name"].append(
                    StudentByNameModel(
                        name=student['name'],
                        student_id=student_id,
                        roll_no=student['roll_no'],
                        email=student['email'],
                        phone_no=student['phone_no']
                    ).dict()
                )

                redis_keys = [
                    student_id,                   # Cache by student_id
                    student['email'],                # Cache by email
                    student['phone_no'],            # Cache by phone number
                    student['roll_no'],             # Cache by roll number
                ]

                for key in redis_keys:
                    message = {
                        "event": "STUDENT_CREATED",
                        "data": {
                            "key": key,
                            "value": student,
                            "method": "insert"
                        }
                    }
                    self.message_broker_repository.publish(topic="student_events", message=message)

                # Cache by course_id using a Redis Set (to avoid overwriting)
                message = {
                    "event": "STUDENT_CREATED",
                    "data": {
                        "key": f"course:{student['course_id']}",
                        "value": student_id,
                        "method": "sadd"
                    }
                }
                self.message_broker_repository.publish(topic="student_events", message=message)

            # Batch insert into Cassandra secondary tables
            for table, data in secondary_data.items():
                self.db_repository.bulk_insert(table=table, data=data)

            # Batch index students in Solr
            for student in prepared_students:
                self.index_student_in_solr(student)

            # Sign up students in the system
            self.bulk_sign_up_students(prepared_students)

        except Exception as e:
            return {"error": f"Error inserting students: {str(e)}", "statusCode": 500}

        return {"success": prepared_students, "statusCode": 200}


    def get_student_by_id(self, student_id: str):
        try:
            student = self.cache_repository.select(table=student_id, conditions="")
            if not student:
                student = self.db_repository.select(table="students", conditions=f"id='{student_id}'")
                if not student:
                    return {"error": "Student not found", "statusCode": 404}
                return {"success": student, "statusCode": 200}
            return {"success": student, "statusCode": 200}
        except Exception as e:
            return {"error": f"Error fetching student: {str(e)}", "statusCode": 500}

    def get_student_by_email(self, email: str):
        try:
            student = self.cache_repository.select(table=email, conditions="")
            if not student:
                student = self.db_repository.select(table="students_by_email", conditions=f"email='{email}'")
                if not student:
                    return {"error": "Student not found", "statusCode": 404}
                fetched_students = []
                for student in student:
                    student_data = self.db_repository.select(table="students", conditions=f"id='{student['student_id']}'")
                    fetched_students.append(student_data[0])
                return {"success": fetched_students, "statusCode": 200}
            return {"success": student, "statusCode": 200}
        except Exception as e:
            return {"error": f"Error fetching student: {str(e)}", "statusCode": 500}


    def get_student_by_roll_no(self, roll_no: str):
        try:
            student = self.cache_repository.select(table=roll_no, conditions="")
            if not student:
                student = self.db_repository.select(table="students_by_roll_no", conditions=f"roll_no='{roll_no}'")
                if not student:
                    return {"error": "Student not found", "statusCode": 404}
                fetched_students = []
                for student in student:
                    student_data = self.db_repository.select(table="students", conditions=f"id='{student['student_id']}'")
                    fetched_students.append(student_data[0])
                return {"success": fetched_students, "statusCode": 200}
            return {"success": student, "statusCode": 200}
        except Exception as e:
            return {"error": f"Error fetching student: {str(e)}", "statusCode": 500}

    def get_student_by_phone_no(self, phone_no: str):
        try:
            student = self.cache_repository.select(table=phone_no, conditions="")
            if not student:
                student = self.db_repository.select(table="students_by_phone_no", conditions=f"phone_no='{phone_no}'")
                if not student:
                    return {"error": "Student not found", "statusCode": 404}
                fetched_students = []
                for student in student:
                    student_data = self.db_repository.select(table="students", conditions=f"id='{student['student_id']}'")
                    fetched_students.append(student_data[0])
                return {"success": fetched_students, "statusCode": 200}
            return {"success": student, "statusCode": 200}
        except Exception as e:
            return {"error": f"Error fetching student: {str(e)}", "statusCode": 500}

    def get_student_by_course(self, course_id: str):
        try:
            student_ids = self.cache_repository.client.smembers(f"course:{course_id}")
            if not student_ids:
                return {"error": "No students found for this course", "statusCode": 404}
            fetched_students = []
            for student_id in student_ids:
                student_data = self.cache_repository.select(table=student_id, conditions="")
                fetched_students.append(student_data)
            return {"success": fetched_students, "statusCode": 200}
        except Exception as e:
            return {"error": f"Error fetching students: {str(e)}", "statusCode": 500}

    def get_student_by_name(self, name: str):
        try:
            students = self.db_repository.select(table="students_by_name", conditions=f"name='{name}'")
            if not students:
                return {"error": "No students found with this name", "statusCode": 404}
            fetched_students = []
            for student in students:
                student_data = self.cache_repository.select(table=student['student_id'], conditions="")
                fetched_students.append(student_data)
            return {"success": fetched_students, "statusCode": 200}
        except Exception as e:
            return {"error": f"Error fetching students: {str(e)}", "statusCode": 500}

    def search_by_name(self, name: str):
        try:
            students = self.search_repository.select(table="students", conditions=f"name:{name}")
            return {"success": students, "statusCode": 200}
        except Exception as e:
            return {"error": f"Error searching students: {str(e)}", "statusCode": 500}

    def search_by_email(self, email: str):
        try:
            students = self.search_repository.select(table="students", conditions=f"email:{email}")
            return {"success": students, "statusCode": 200}
        except Exception as e:
            return {"error": f"Error searching students: {str(e)}", "statusCode": 500}

    def get_all_students(self):
        try:
            students = self.db_repository.select(table="students", conditions="")
            return {"success": students, "statusCode": 200}
        except Exception as e:
            return {"error": f"Error fetching students: {str(e)}", "statusCode": 500}

    def clear_all_data(self):
        try:
            self.db_repository.remove_all_data()
            self.cache_repository.remove_all_data()
            self.search_repository.remove_all_data()
            return {"success": "All data cleared", "statusCode": 200}
        except Exception as e:
            return {"error": f"Error clearing data: {str(e)}", "statusCode": 500}
