from app import *
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"

def test_get_authors(client, mock_app_manager):
    mock_app_manager.authors_manager.add_author("Alice", "http://example.com/author1")
    response = client.get("/authors")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == [{"author": "Alice", "img": "http://example.com/author1"}]