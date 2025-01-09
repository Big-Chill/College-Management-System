from pydantic import BaseModel, validator, Field
from typing import Dict
from uuid import uuid1
from .base_model import IModel

class CourseModel(BaseModel, IModel):
    course_name: str
    course_description: str
    course_credits: int
    course_duration: int
    course_duration_unit: str
    id: str = Field(default_factory=lambda: f'course{uuid1()}')

    def get_id(self) -> str:
        return self.id

    @validator("course_duration_unit")
    def validate_course_duration_unit(cls, v):
        if v not in ["days", "weeks", "months", "years"]:
            raise ValueError("Invalid course duration unit")
        return v

    def validate_and_prepare_data(self, payload: Dict) -> Dict:
        # Validate the required fields
        required_fields = ["course_name", "course_description", "course_credits", "course_duration", "course_duration_unit"]
        for field in required_fields:
            if field not in payload:
                raise ValueError(f"Missing required field: {field}")

        # Additional validations (e.g., validate course credits and duration)
        if not isinstance(payload["course_credits"], int) or payload["course_credits"] <= 0:
            raise ValueError("Course credits must be a positive integer.")

        if not isinstance(payload["course_duration"], int) or payload["course_duration"] <= 0:
            raise ValueError("Course duration must be a positive integer.")

        # Validate the course duration unit
        if payload["course_duration_unit"] not in ["days", "weeks", "months", "years"]:
            raise ValueError("Invalid course duration unit.")

        # Prepare the final data with the generated ID
        prepared_data = self.dict()  # Convert the model to a dictionary
        prepared_data["id"] = self.id  # Add the generated ID

        return prepared_data


class CourseDurationLookupModel(BaseModel):
    course_duration: int
    course_duration_unit: str
    course_id: str

class CourseByName(BaseModel):
    course_name: str
    course_id: str
    course_description: str

class CourseByCredits(BaseModel):
    course_credits: int
    course_id: str
    course_name: str
    course_duration: int
    course_duration_unit: str
