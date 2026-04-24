import multiprocessing
import pytchat
import time
import re
import random


class AuthorsManager:
    def __init__(self, authors_dict):
        self.authors_dict = authors_dict if authors_dict is not None else {}  # Zarządzany zbiór

    def add_author(self, author_name, author_img=None):
        self.authors_dict[author_name] = {"author": author_name, "img": author_img}
    
    def delete_author(self, author_name):
        if author_name in self.authors_dict:
            del self.authors_dict[author_name]

    def get_authors(self):
        return self.authors_dict

    def draw_winner(self):
        if not self.authors_dict:
            return None
        return random.choice(list(self.authors_dict.values()))

    def clear_authors(self):
        self.authors_dict.clear()

class AppManager:
    def __init__(self):
        self.authors_manager = AuthorsManager()
        self.stop_event = multiprocessing.Event()
        self.process = None
        self.fetching = False
        self.from_main_to_listener_queue = multiprocessing.Queue()  # Kolejka do komunikacji z procesem nasłuchującym
        self.from_listener_to_main_queue = multiprocessing.Queue()  # Kolejka do komunikacji z procesem nasłuchującym

    def run_process(self, video_url):
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

    def start_chat_fetching_process(self, video_url):
        if self.process is not None and self.process.is_alive():
            self.terminate_process() # Zakończ istniejący proces, jeśli jest aktywny
        self.authors_manager.clear_authors()  # Resetujemy zarządzany zbiór
        self.stop_event.clear()  # Resetujemy zdarzenie stop
        self.run_process(video_url)
    
    def terminate_process(self):
        if self.process and self.process.is_alive():
            self.stop_fetching_authors()  # Ustawiamy zdarzenie stop, aby proces mógł się zamknąć
            self.from_main_to_listener_queue.put({"status": "shutdown"})  # Wysyłamy sygnał do procesu, aby się zamknął
            self.process.join(timeout=3) # Dajemy mu czas na łagodne zamknięcie
        if self.process and self.process.is_alive(): # Sprawdzamy ponownie, czy nadal żyje
            self.process.terminate()  # Jeśli nie zamknął się łagodnie, wymuszamy zamknięcie
        self.process = None # Resetujemy referencję do procesu
    
    def stop_fetching_authors(self):
        self.stop_event.set()  # Ustawiamy zdarzenie stop


def get_video_id(url):
        """
        Wyciąga Video ID z różnych formatów linków YouTube:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/live/VIDEO_ID
        - https://youtube.com/shorts/VIDEO_ID
        """
        pattern = r'(?:v=|\/|shorts\/|live\/)([0-9A-Za-z_-]{11})(?:[&?]|$)'
        match = re.search(pattern, url)

        if match:
            return match.group(1)
        return None

def create_chat_connection(url):
        try:
            video_id = get_video_id(url)
            if not video_id:
                print(f"DEBUG: Could not extract video_id from {url}")
                return None
            chat = pytchat.create(video_id=video_id)
            return chat
        except Exception as e:
            print(f"DEBUG: Error creating chat connection: {e}")
            return None
        
def apply_url(url, from_listener_to_main_queue):
        video_id = get_video_id(url)
        if not video_id:
             from_listener_to_main_queue.put({"success": False, "message": "Niepoprawny format linku YouTube"})
             return None

        chat = create_chat_connection(url)
        if chat is None:
            from_listener_to_main_queue.put({"success": False, "message": "Błąd połączenia z czatem (IP zablokowane?)"})
            return None
        from_listener_to_main_queue.put({"success": True, "message": "Listener started"})
        return chat

def start_chat_listener(video_url, stop_event, authors_manager, from_main_to_listener_queue, from_listener_to_main_queue):
        """
        Funkcja nasłuchująca czat, działająca w osobnym procesie.
        Dodaje unikalnych autorów do authors_list.
        """
        chat = apply_url(video_url, from_main_to_listener_queue, from_listener_to_main_queue)
        if not chat:
            return  # Jeśli URL jest nieprawidłowy, kończymy funkcję
        
        while True:
            status = from_main_to_listener_queue.get()
            if status.get("status") == "shutdown":
                break
            stop_event.clear()
            while not stop_event.is_set() and chat.is_alive():
                try:
                    for c in chat.get().sync_items():
                        message = c.message
                        keyword = status.get("keyword")
                        if check_keyword_in_message(message, keyword):
                            authors_manager.add_author(c.author.name, c.author.imageUrl)
                except Exception as e:
                    pass # Można dodać logowanie błędu, jeśli jest to potrzebne

def check_keyword_in_message(message, keyword):
    return not keyword or keyword.lower() in message.lower()