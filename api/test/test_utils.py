# api/test/test_utils.py
import pytest
from api.routers.utils import get_password_hash, verify_password, create_access_token, decode_access_token
from datetime import timedelta

def test_get_password_hash():
    password = "mysecretpassword"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert verify_password(password, hashed_password)

def test_verify_password():
    password = "mysecretpassword"
    wrong_password = "wrongpassword"
    hashed_password = get_password_hash(password)
    assert verify_password(password, hashed_password)
    assert not verify_password(wrong_password, hashed_password)

def test_create_access_token():
    data = {"sub": "test@example.com", "user_id": 1}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=1))
    assert token is not None

def test_decode_access_token():
    data = {"sub": "test@example.com", "user_id": 1}
    token = create_access_token(data=data, expires_delta=timedelta(minutes=1))
    payload = decode_access_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["user_id"] == 1

def test_expired_access_token():
    data = {"sub": "test@example.com", "user_id": 1}
    token = create_access_token(data=data, expires_delta=timedelta(seconds=-1))
    payload = decode_access_token(token)
    assert payload is None

def test_invalid_access_token():
    token = "invalidtoken"
    payload = decode_access_token(token)
    assert payload is None
