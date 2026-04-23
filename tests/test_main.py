from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API Mockup Service is running", "docs": "/docs"}

def test_swagger_ui_exists():
    response = client.get("/swagger")
    assert response.status_code == 200
