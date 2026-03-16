import multiprocessing
import pytchat
import time
import re

stop_event_global = multiprocessing.Event() # Zmieniona nazwa, żeby nie kolidować z argumentem funkcji

class AuthorsManager:
    def __init__(self):
        self.authors_set = multiprocessing.Manager().set()  # Zarządzany zbiór

    def add_author(self, author_name):
        if author_name not in self.authors_set:
            self.authors_set.add(author_name)
    
    def delete_author(self, author_name):
        if author_name in self.authors_set:
            self.authors_set.remove(author_name)
    
    def get_authors(self):
        return self.authors_set

class AppManager:
    def __init__(self):
        self.authors_manager = AuthorsManager()
        self.stop_event = multiprocessing.Event()
        self.process = None

    def start_listener(self):
        self.authors_manager.clear_all()  # Resetujemy zarządzany zbiór
        self.stop_event.clear()  # Resetujemy zdarzenie stop
        self.process = multiprocessing.Process(target=start_chat_listener, args=(self.video_url, self.stop_event, self.authors_manager))
        self.process.start()
    
    def stop_listener(self):
        self.stop_event.set()  # Ustawiamy zdarzenie stop
        if self.process is not None:
            self.process.join(timeout=3)
        if self.process:
            self.process.terminate()  # Czekamy na zakończenie procesu

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

def validate_video_url(url):
        """
        Waliduje, czy podany URL jest poprawnym linkiem do filmu na YouTube.
        Zwraca True, jeśli URL jest poprawny, w przeciwnym razie False.
        """
        video_id = get_video_id(url)
        chat = pytchat.create(video_id=video_id)
        return chat.is_alive()

def start_chat_listener(video_url, stop_event, authors_manager):
        """
        Funkcja nasłuchująca czat, działająca w osobnym procesie.
        Dodaje unikalnych autorów do authors_list.
        """
        video_id = get_video_id(video_url)
        chat = pytchat.create(video_id=video_id)
        while not stop_event.is_set() and chat.is_alive():
            try:
                for c in chat.get().sync_items():
                    if c.author.name not in authors_manager.get_authors():
                        authors_manager.add_author(c.author.name)
            except Exception as e:
                # print(f"Błąd podczas pobierania komentarzy: {e}") # Usunięte drukowanie, aby nie zaśmiecać konsoli
                pass # Można dodać logowanie błędu, jeśli jest to potrzebne
            time.sleep(0.5) # Krótka pauza, aby nie przeciążać CPU