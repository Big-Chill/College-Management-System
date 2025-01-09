import re
from uuid import uuid1
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Dict
from datetime import date
from .base_model import IModel

class StudentModel(BaseModel, IModel):
    name: str
    roll_no: str
    dob_day: int
    dob_month: int
    dob_year: int
    email: EmailStr
    phone_no: str
    enrollment_type: str
    enrollment_year: int
    enrollment_month: int
    enrollment_day: int
    course: str
    course_id: str
    id: str = Field(default_factory=lambda: f'student{uuid1()}')

    def get_id(self) -> str:
        return self.id

    # Calculate age dynamically based on the date of birth
    @property
    def age(self) -> int:
        today = date.today()
        return today.year - self.dob_year - ((today.month, today.day) < (self.dob_month, self.dob_day))

    # Validate email format and uniqueness
    @validator("email")
    def validate_email(cls, v):
        # Ensure the email matches a valid pattern
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, v):
            raise ValueError("Invalid email format")
        return v

    # Validate phone number
    @validator("phone_no")
    def validate_phone_no(cls, v):
        # Validate that phone number is in the format of digits only and has a certain length
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Phone number must be 10 digits")
        return v

    # Validate date of birth
    @validator("dob_day", "dob_month", "dob_year")
    def validate_dob(cls, v, values, field):
        # Ensure valid day, month, and year for DOB
        if field.name == "dob_day":
            if not (1 <= v <= 31):
                raise ValueError("Invalid day value")
        elif field.name == "dob_month":
            if not (1 <= v <= 12):
                raise ValueError("Invalid month value")
        elif field.name == "dob_year":
            current_year = date.today().year
            if v > current_year or v < (current_year - 120):  # reasonable upper bound for age
                raise ValueError(f"Invalid year value. Year should be between {current_year-120} and {current_year}")
        return v

    # Check for valid enrollment type (this is a basic example, expand as needed)
    @validator("enrollment_type")
    def validate_enrollment_type(cls, v):
        if v not in ["Full-Time", "Part-Time", "Online"]:
            raise ValueError("Invalid enrollment type. It should be one of: Full-Time, Part-Time, Online.")
        return v

    def validate_and_prepare_data(self, payload: Dict) -> Dict:
        # Validate required fields
        required_fields = ["name", "roll_no", "dob_day", "dob_month", "dob_year", "email",
                        "phone_no", "enrollment_type", "enrollment_year", "enrollment_month",
                        "enrollment_day", "course", "course_id"]
        for field in required_fields:
            if field not in payload:
                raise ValueError(f"Missing required field: {field}")

        # Prepare the data with the generated ID
        prepared_data = self.dict()  # Convert model to dictionary
        prepared_data["id"] = self.id  # Ensure the ID is added properly
        return prepared_data

# Lookup Table Models

class StudentByEmailModel(BaseModel):
    email: str
    student_id: str

class StudentByRollNoModel(BaseModel):
    roll_no: str
    student_id: str

class StudentByPhoneNoModel(BaseModel):
    phone_no: str
    student_id: str

class StudentByCourseModel(BaseModel):
    course_id: str
    student_id: str
    name: str
    roll_no: str
    email: str
    phone_no: str

class StudentByNameModel(BaseModel):
    name: str
    student_id: str
    roll_no: str
    email: str
    phone_no: str

class StudentByUserModel(BaseModel):
    roll_no: str
    user_id: str
