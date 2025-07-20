from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from news_aggregator.main import app
from news_aggregator.database import Base, get_db,engine  # <-- correct Base
from news_aggregator import models, crud

import pytest

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

# Test helper
db = next(override_get_db())




def test_get_existing_user():
    test_user = models.User(
        email="user1@example.com",
        username="user1",
        first_name="Test1",
        last_name="Case1",
        password="password1"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    user = crud.get_user_by_email("user1@example.com", db)
    assert user is not None
    assert user.email == "user1@example.com"


def test_get_userby_email_with_empty_string():
    test_user = models.User(
        email="user2@example.com",
        username="user2",
        first_name="Test2",
        last_name="Case2",
        password="password2"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    user = crud.get_user_by_email("", db)
    assert user is None


def test_user_email_with_none():
    with pytest.raises(TypeError):
        crud.get_user_by_email(None, db)


def test_user_email_with_case_sensitive():
    test_user = models.User(
        email="CaseSensitive@Example.com",
        username="user3",
        first_name="Test3",
        last_name="Case3",
        password="password3"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    result = crud.get_user_by_email("casesensitive@example.com", db)
    assert result is None


def test_get_user_by_email_with_whitespace():
    test_user = models.User(
        email="user4@example.com",
        username="user4",
        first_name="Test4",
        last_name="Case4",
        password="password4"
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    result = crud.get_user_by_email("  user4@example.com", db)
    assert result is not None
    assert result.email == "user4@example.com"
