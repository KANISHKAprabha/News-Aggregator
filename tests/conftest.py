import pytest
from sqlalchemy import create_engine
from news_aggregator.database import Base, get_db
TEST_DATABASE_URL="sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

@pytest.fixture(autouse=True)
def clear_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)