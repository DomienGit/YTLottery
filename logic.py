import pytchat
import re
import random

class CommentAuthors:
    def __init__(self):
        self.authors = set()  # Używamy zbioru, aby uniknąć duplikatów

    def add_author(self, author):
        self.authors.add(author)

    def get_authors(self):
        return self.authors

    def delete_author(self, author):
        self.authors.discard(author)

def get_video_id(url):
     """
     Wyciąga Video ID z różnych formatów linków YouTube.
     Zwraca ID (11 znaków) lub None, jeśli link jest niepoprawny.
     """
     pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?]|$)'
     match = re.search(pattern, url)

     if match:
         return match.group(1)
     return None

def collect_comments(video_url, author_manager):
    try:
        video_id = get_video_id(video_url)
        if not video_id:
            return False

        chat = pytchat.create(video_id=video_id)
        while chat.is_alive():
            for c in chat.get().sync_items():
                print(f"{c.author.name}")
                author_manager.add_author(c.author.name)

    except Exception as e:
        return False

def pick_random_author(author_manager):
    authors = list(author_manager.get_authors())
    if not authors:
        return None
    return random.choice(authors)

