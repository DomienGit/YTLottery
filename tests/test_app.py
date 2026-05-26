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

def test_add_author(client, mock_app_manager):
    response = client.post("/add-author", json={"name": "Bob"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Author 'Bob' added"
    assert mock_app_manager.authors_manager.get_authors() == {"Bob": {"author": "Bob", "img": None}}

def test_delete_author(client, mock_app_manager):
    mock_app_manager.authors_manager.add_author("Bob", "http://example.com/author2")
    response = client.post("/delete", json={"name": "Bob"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Author 'Bob' deleted"
    assert mock_app_manager.authors_manager.get_authors() == {}

def test_clear_authors(client, mock_app_manager):
    mock_app_manager.authors_manager.add_author("Alice", "http://example.com/author1")
    mock_app_manager.authors_manager.add_author("Bob", "http://example.com/author2")
    response = client.post("/clear")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "All authors cleared"
    assert mock_app_manager.authors_manager.get_authors() == {}

def test_draw_winner_with_authors(client, mock_app_manager):
    mock_app_manager.authors_manager.add_author("Alice", "http://example.com/author1")
    mock_app_manager.authors_manager.add_author("Bob", "http://example.com/author2")
    response = client.post("/draw")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Winner drawn"
    assert data["winner"] not in ["Alice", "Bob"]
    assert data["img"] in ["http://example.com/author1", "http://example.com/author2"]

def test_draw_winner_no_authors(client):
    response = client.post("/draw")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False
    assert data["message"] == "No authors to draw from"

def test_apply_url_no_url(client):
    response = client.post("/apply-url", json={"url": ""})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False
    assert data["message"] == "Type a video URL"

def test_apply_url_invalid_url(client, mock_app_manager):
    mock_app_manager.from_listener_to_main_queue.get.return_value = {"success": False, "message": "Invalid video URL"}
    response = client.post("/apply-url", json={"url": "invalid_url"})
    assert response.status_code == 200
    data = response.json()
    mock_app_manager.start_chat_fetching_process.assert_called_once_with("invalid_url")
    assert data["success"] == False
    assert data["message"] == "Invalid video URL"

def test_apply_url_valid_url(client, mock_app_manager):
    mock_app_manager.from_listener_to_main_queue.get.return_value = {"success": True, "message": "Video URL validated"}
    response = client.post("/apply-url", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    assert response.status_code == 200
    data = response.json()
    mock_app_manager.start_chat_fetching_process.assert_called_once_with("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert data["success"] == True
    assert data["message"] == "Video URL validated"
    assert data["url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def test_start_listener_no_keyword(client, mock_app_manager):
    response = client.post("/start", json={"keyword": ""})
    assert response.status_code == 200
    data = response.json()
    mock_app_manager.from_main_to_listener_queue.put.assert_called_once_with({"status": "start", "keyword": ""})
    assert data["success"] == True
    assert data["message"] == "Chat listener started"

def test_start_listener_with_keyword(client, mock_app_manager):
    response = client.post("/start", json={"keyword": "test"})
    assert response.status_code == 200
    data = response.json()
    mock_app_manager.from_main_to_listener_queue.put.assert_called_once_with({"status": "start", "keyword": "test"})
    assert data["success"] == True
    assert data["message"] == "Chat listener started"

def test_stop_listener(client, mock_app_manager):
    response = client.post("/stop")
    assert response.status_code == 200
    data = response.json()
    mock_app_manager.stop_fetching_authors.assert_called_once()
    assert data["success"] == True
    assert data["message"] == "Chat listener stopped"