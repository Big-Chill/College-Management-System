import re
from uuid import uuid1
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Dict
from datetime import date
from .base_model import IModel

class TeacherModel(BaseModel, IModel):
    name:str
    employee_no:str
    dob_day: int
    dob_month: int
    dob_year: int
    email: EmailStr
    phone_no: str
    course: str
    course_id: str
    id: str = Field(default_factory=lambda: f'teacher{uuid1()}')

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

    def validate_and_prepare_data(self, payload: Dict) -> Dict:
        required_fields = ["name", "employee_no", "dob_day", "dob_month", "dob_year", "email", "phone_no", "course", "course_id"]
        for field in required_fields:
            if field not in payload:
                raise ValueError(f"{field} is required")

        prepared_data = self.dict()  # Convert model to dictionary
        prepared_data["id"] = self.id  # Ensure the ID is added properly
        return prepared_data