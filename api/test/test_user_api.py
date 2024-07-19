# api/test/test_user_api.py
import pytest
from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch
import uuid

client = TestClient(app)

@pytest.fixture
def mock_db_connection(memory_db):
    with patch("api.database.get_db_connection", return_value=memory_db):
        yield memory_db

def test_create_user(mock_db_connection):
    unique_pseudo = f"testuser_{uuid.uuid4()}"
    unique_email = f"test_{uuid.uuid4()}@example.com"

    response = client.post("/users/create", json={
        "pseudo": unique_pseudo,
        "email": unique_email,
        "password": "password123"
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert "user_id" in data
    assert data["pseudo"] == unique_pseudo
    assert data["email"] == unique_email

def test_login_user(mock_db_connection):
    unique_pseudo = f"testuser_{uuid.uuid4()}"
    unique_email = f"test_{uuid.uuid4()}@example.com"

    response = client.post("/users/create", json={
        "pseudo": unique_pseudo,
        "email": unique_email,
        "password": "password123"
    })
    assert response.status_code == 200, response.text

    response = client.post("/users/login", json={
        "pseudo": unique_pseudo,
        "password": "password123"
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
