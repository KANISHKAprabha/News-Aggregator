import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt



ACCESS_TOKEN_EXPIRE_SECONDS = -1
REFRESH_TOKEN_EXPIRE_SECONDS = -1
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')   # should be kept secret
JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET_KEY')    # should be kept secret



def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
  try:
    if expires_delta is not None:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt
  except Exception as e:
    print(f"Error creating access token: {e}")
    raise e

def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(seconds=REFRESH_TOKEN_EXPIRE_SECONDS)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt



def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])