from logic import get_video_id, check_keyword_in_message, AuthorsManager
import pytest

@pytest.mark.parametrize("url, expected", [
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/live/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?time_continue=1&v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1s", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL1234567890", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&index=1", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley&feature=share", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?time_continue=1&v=dQw4w9WgXcQ&feature=share", "dQw4w9WgXcQ"),
    ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=1s&feature=share", "dQw4w9WgXcQ")
])
def test_get_video_id(url, expected):
    assert get_video_id(url) == expected

@pytest.mark.parametrize("message, keyword, expected", [
    ("This is a test message", "test", True),
    ("This is a test message", "TEST", True),
    ("This is a test message", "message", True),
    ("This is a test message", "notfound", False),
    ("This is a test message", "", True)
])
def test_check_keyword_in_message(message, keyword, expected):
    assert check_keyword_in_message(message, keyword) == expected

@pytest.fixture
def authors():
    authors_manager = AuthorsManager()
    yield authors_manager
    authors_manager.clear_authors()

def test_add_author(authors):
    authors.add_author("Alice", "http://example.com/alice.jpg")
    assert "Alice" in authors.get_authors()
    assert authors.get_authors()["Alice"]["author"] == "Alice"
    assert "NotIn" not in authors.get_authors()

def test_delete_author(authors):
    authors.add_author("Alice", "http://example.com/alice.jpg")
    authors.delete_author("Alice")
    assert "Alice" not in authors.get_authors()

def test_draw_winner_returned_winner(authors):
    authors.add_author("Alice", "http://example.com/alice.jpg")
    winner = authors.draw_winner()
    assert winner["author"] == "Alice"

def test_draw_winner_empty_authors(authors):
    winner = authors.draw_winner()
    assert winner is None

def test_clear_authors(authors):
    authors.add_author("Alice", "http://example.com/alice.jpg")
    authors.clear_authors()
    assert len(authors.get_authors()) == 0