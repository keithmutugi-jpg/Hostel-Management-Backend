from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json()["message"]

def test_invalid_route():
    response = client.get("/invalid-route")
    assert response.status_code == 404

def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()

def test_login_missing_fields():
    response = client.post("/auth/login", json={})
    assert response.status_code in [400, 422]