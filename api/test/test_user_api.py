# api/test/test_user_api.py

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

@pytest.fixture
def test_db_connection(mocker):
    mock_db = mocker.patch("api.database.get_db_connection").return_value
    mock_db.execute.return_value.fetchone.side_effect = [None, {"user_id": 1, "pseudo": "testuser", "email": "test@example.com", "password": "$2b$12$KIXxV6rY2ie93mFT5W7KXe9/EZZrS3NHsdZVbGAZc5zDdXB0bBfUy"}]
    mock_db.commit.return_value = None
    return mock_db

def test_create_user(test_db_connection):
    response = client.post("/users/create", json={
        "pseudo": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert "user_id" in data
    assert data["pseudo"] == "testuser"
    assert data["email"] == "test@example.com"

def test_login_user(test_db_connection):
    # First create the user
    client.post("/users/create", json={
        "pseudo": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })

    # Then try to login
    response = client.post("/users/login", json={
        "pseudo": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
