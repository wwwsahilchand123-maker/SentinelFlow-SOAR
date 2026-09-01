import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app as fastapi_app
from app.database import Base, get_db
from app.seed import seed_database
import app.seed as seed_module

TEST_DATABASE_URL = "sqlite:///./test_soar.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

fastapi_app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Bind test engine
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    orig_session = seed_module.SessionLocal
    orig_engine = seed_module.engine
    seed_module.SessionLocal = TestingSessionLocal
    seed_module.engine = test_engine
    
    seed_database()
    
    seed_module.SessionLocal = orig_session
    seed_module.engine = orig_engine
    
    yield
    
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("test_soar.db"):
        try:
            os.remove("test_soar.db")
        except Exception:
            pass

@pytest.fixture
def client():
    return TestClient(fastapi_app)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
