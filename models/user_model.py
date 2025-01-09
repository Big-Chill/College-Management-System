import re
from pydantic import BaseModel, Field
from uuid import uuid1
from typing import Dict
from datetime import date
from .base_model import IModel


class UserModel(BaseModel, IModel):
  user_name: str
  password: str
  default_password: str = Field(default_factory=lambda: 'wanted-note')
  email: str
  reference_id: str
  id: str = Field(default_factory=lambda: f'user{uuid1()}')

  def get_id(self):
    return self.id

  def getDefaultPassword(self):
    return self.defaultPassword

  def validate_and_prepare_data(self):
    # Validate email format and uniqueness
    email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if not re.match(email_regex, self.email):
      raise ValueError("Invalid email format")
    return self

class UserByUserNameModel(BaseModel):
  user_name: str
  password: str
  user_id: str
  reference_id: str