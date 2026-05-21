from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest
from app import *
from logic import AuthorsManager, AppManager
import queue
import threading

client = TestClient(app)

@pytest.fixture
def authors():
    authors_manager = AuthorsManager()
    yield authors_manager
    authors_manager.clear_authors()

@pytest.fixture
def mock_app_manager():
    manager = MagicMock()
    manager.authors_manager = AuthorsManager()
    manager.from_listener_to_main_queue = MagicMock()
    manager.from_main_to_listener_queue = MagicMock()   
    return manager

@pytest.fixture
def client(mock_app_manager):
    app.dependency_overrides[get_app_manager] = lambda: mock_app_manager
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def app_manager():
    manager = AppManager(
        authors_manager=AuthorsManager({}),
        stop_event=threading.Event(),
        from_listener_to_main_queue=queue.Queue(),
        from_main_to_listener_queue=queue.Queue()
    )
    return manager

@pytest.fixture
def integration_client(app_manager):
    app.dependency_overrides[get_app_manager] = lambda: app_manager
    yield TestClient(app)
    app.dependency_overrides.clear()