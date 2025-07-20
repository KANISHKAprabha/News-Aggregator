import os
from datetime import timedelta, datetime
import time
from jose import ExpiredSignatureError, jwt, JWTError
import pytest
from news_aggregator import utils


os.environ["JWT_SECRET_KEY"] = "test_secret_key"
os.environ["JWT_REFRESH_SECRET_KEY"] = "test_refresh_secret_key"


import importlib
importlib.reload(utils)


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
ALGORITHM = "HS256"


def test_create_access_token_valid():
    token = utils.create_access_token("test@example.com")
    payload = jwt.decode(token,JWT_SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"]=="test@example.com"
    assert "exp" in payload
    assert datetime.fromtimestamp(payload["exp"]) > datetime.now()



def test_create_access_token_invalid():
    token = utils.create_access_token("test@example.com", timedelta(seconds=-1,days=0,minutes=0))
    payload = jwt.decode(token,JWT_SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"]!="testttu@example.com"
    print(payload["exp"],"line no 30 in test_utils.py")
    assert "exp" in payload
    assert datetime.fromtimestamp(payload["exp"]) < datetime.now()


def test_create_access_token_invalid_expiration():
    token = utils.create_access_token("test@example.com",timedelta(seconds=-1))
    print(token,"line no 41 in test_utils.py")
    print("Current system time:", datetime.now())
    time.sleep(1) 
    with pytest.raises(ExpiredSignatureError):
        jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])


