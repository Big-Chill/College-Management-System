from datetime import datetime, timedelta
from jose import JWTError, jwt
from configuration import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import HTTPException, status

class Jwt:
  def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

  def verify_access_token(token: str):
    try:
      payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
      return payload
    except JWTError:
      raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")



