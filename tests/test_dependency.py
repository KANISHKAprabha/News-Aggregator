from news_aggregator.utils import JWT_SECRET_KEY, ALGORITHM
from jose import jwt
from datetime import datetime, timedelta
import pytest
from fastapi import Request,    HTTPException
from fastapi.testclient import TestClient
from news_aggregator.dependency import get_token_from_cookie, get_current_user
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from news_aggregator.main import app
from news_aggregator.database import Base, get_db, engine  # <-- correct Base
from news_aggregator import models, crud, schemas

# Test database
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)

# Dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)
db = next(override_get_db())

def create_jwt_token(email:str):
    expire = datetime.now() + timedelta(minutes=15)
    to_encode ={"sub":email,"exp":expire}
    return jwt.encode(to_encode,    JWT_SECRET_KEY,algorithm=ALGORITHM)






def test_get_existing_user():
    test_user = models.User(
        email="keelllu@gmail.com",
        username="keelllu",
        first_name="keppasathh",
        last_name="keppasathh",
        password="password1"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    user = crud.get_user_by_email("keelllu@gmail.com", db)
    assert user is not None
    assert user.email == "keelllu@gmail.com"






def test_get_token_from_cookie_missing():
    scope={
        "type":"http",
        "headers":[],
        "method":"GET",
        "path":"/",
        "query_string":b"",
    }
    req = Request(scope=scope)
    with pytest.raises(HTTPException) as exc_info:
        get_token_from_cookie(request=req)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"


def test_check_for_non_user_home_page():
    
    token = create_jwt_token("kaniii@gmail.com")
    response = client.cookies.set("access_token", token)
    response = client.get("/")  # Replace with an actual endpoint that requires authentication
    print(response.json(),"line no 58")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

    

def create_expired_token(email:str):
    payload={
        "sub":email,
        "exp":datetime.now()-timedelta(minutes=0)  

    }
    return jwt.encode(payload,JWT_SECRET_KEY,algorithm=ALGORITHM)


def test_user_with_expired_token_home_page():
    token = create_expired_token("keelllu@gmail.com")
    client.cookies.set("access_token", token)
    response = client.get("/") 
    assert response.status_code == 200 
    
    
