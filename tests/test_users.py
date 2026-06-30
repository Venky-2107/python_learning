from fastapi.testclient import TestClient
from main import app
from database import Base, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import get_db
from fastapi import Depends
import pytest

# create a separate test database
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

# override the get_db dependency to use test DB
def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# create tables fresh before tests
Base.metadata.create_all(bind=test_engine)

@pytest.fixture(autouse=True, scope='session')
def reset_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield

client = TestClient(app)

def test_register_user():
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "123456"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    
def test_register_duplicate_user():
    response = client.post('/auth/register', json={
        "name": "New test user duplicate",
        "email": "test@example.com",
        "password": '12345'
    })
    
    assert response.status_code == 400
    assert response.json()['detail'] == "Email already registered"

def test_login_user():
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "123456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password():
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    
def test_get_users_without_token():
    response = client.get('/users')
    
    assert response.status_code == 401