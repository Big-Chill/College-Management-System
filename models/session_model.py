import re
from pydantic import BaseModel, Field
from uuid import uuid4
from .base_model import IModel
from datetime import timedelta, datetime

class SessionModel(BaseModel, IModel):
  user_id: str
  session_id: str = Field(default_factory=lambda: 'session'+str(uuid4()))  # Using UUID for session_id
  created_at: int = Field(default_factory=lambda: int(datetime.now().timestamp()))  # Epoch timestamp (seconds since 1970)
  expires_at: int = Field(default_factory=lambda: int((datetime.now() + timedelta(days=1)).timestamp()))  # Default expiration (1 day)
  last_accessed_timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp()))  # Epoch timestamp (seconds since 1970)


  def get_id(self):
    return self.session_id

  def validate_and_prepare_data(self):
    return self