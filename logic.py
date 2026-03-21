import multiprocessing
import pytchat
import time
import re
import random


class AuthorsManager:
    def __init__(self):
        self.authors_set = multiprocessing.Manager().set()  # Zarządzany zbiór

    def add_author(self, author_name):
        self.authors_set.add(author_name)
    
    def delete_author(self, author_name):
        if author_name in self.authors_set:
            self.authors_set.remove(author_name)
    
    def get_authors(self):
        return set(self.authors_set)

    def draw_winner(self):
        if not self.authors_set:
            return None
        return random.choice(list(self.authors_set))
    
    def clear_authors(self):
        self.authors_set.clear()

class AppManager:
    def __init__(self):
        self.authors_manager = AuthorsManager()
        self.stop_event = multiprocessing.Event()
        self.process = None
        self.fetching = False
        self.from_main_to_listener_queue = multiprocessing.Queue()  # Kolejka do komunikacji z procesem nasłuchującym
        self.from_listener_to_main_queue = multiprocessing.Queue()  # Kolejka do komunikacji z procesem nasłuchującym

    def start_listener(self, video_url):
        self.authors_manager.clear_authors()  # Resetujemy zarządzany zbiór
        self.stop_event.clear()  # Resetujemy zdarzenie stop
        self.process = multiprocessing.Process(
             target=start_chat_listener, 
             args=(
                  video_url, 
                  self.stop_event, 
                  self.authors_manager, 
                  self.from_main_to_listener_queue, 
                  self.from_listener_to_main_queue
                  )
            )
        self.process.start()
    
    def stop_listener(self):
        self.stop_event.set()  # Ustawiamy zdarzenie stop
        if self.process and self.process.is_alive():
            self.from_main_to_listener_queue.put({"command": "shutdown"})
            self.process.join(timeout=3) # Dajemy mu czas na łagodne zamknięcie
        if self.process and self.process.is_alive(): # Sprawdzamy ponownie, czy nadal żyje
            self.process.terminate()  # Jeśli nie zamknął się łagodnie, wymuszamy zamknięcie
        self.process = None # Resetujemy referencję do procesu

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

def create_chat_connection(url):
        # try:
        video_id = get_video_id(url)
        chat = pytchat.create(video_id=video_id)
        return chat, video_id
        # except:
        #     return None

def start_chat_listener(video_url, stop_event, authors_manager, from_main_to_listener_queue, from_listener_to_main_queue):
        """
        Funkcja nasłuchująca czat, działająca w osobnym procesie.
        Dodaje unikalnych autorów do authors_list.
        """
        chat, video_id = create_chat_connection(video_url)
        if chat is None:
            from_listener_to_main_queue.put({"success": False, "message": f"Invalid video URL: {video_id}"})
            return None
        from_listener_to_main_queue.put({"success": True, "message": "Listener started"})

        command = from_main_to_listener_queue.get()
        if command.get("command") == "shutdown":
            return 
        while True:
            
            while not stop_event.is_set() and chat.is_alive():
                try:
                    for c in chat.get().sync_items():
                        authors_manager.add_author(c.author.name)
                except Exception as e:
                    # print(f"Błąd podczas pobierania komentarzy: {e}") # Usunięte drukowanie, aby nie zaśmiecać konsoli
                    pass # Można dodać logowanie błędu, jeśli jest to potrzebne
                time.sleep(0.5) # Krótka pauza, aby nie przeciążać CPU