import multiprocessing
import pytchat
import time
import re

stop_event_global = multiprocessing.Event() # Zmieniona nazwa, żeby nie kolidować z argumentem funkcji

def _get_video_id(url):
     """
     Wyciąga Video ID z różnych formatów linków YouTube.
     Zwraca ID (11 znaków) lub None, jeśli link jest niepoprawny.
     """
     pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?]|$)'
     match = re.search(pattern, url)

     if match:
         return match.group(1)
     return None

def start_chat_listener(video_id, authors_list, stop_event):
    """
    Funkcja nasłuchująca czat, działająca w osobnym procesie.
    Dodaje unikalnych autorów do authors_list.
    """
    chat = pytchat.create(video_id=video_id)
    while not stop_event.is_set() and chat.is_alive():
        try:
            for c in chat.get().sync_items():
                if c.author.name not in authors_list:
                    authors_list.append(c.author.name)
        except Exception as e:
            # print(f"Błąd podczas pobierania komentarzy: {e}") # Usunięte drukowanie, aby nie zaśmiecać konsoli
            pass # Można dodać logowanie błędu, jeśli jest to potrzebne
        time.sleep(0.5) # Krótka pauza, aby nie przeciążać CPU

# Oryginalny blok if __name__ == "__main__": zostaje w app_no_streamlit.py, ale nie będzie używany przez Streamlit
if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        authors_set = manager.list()  # Tworzymy zarządzany zbiór
        video_url = input("Podaj link do filmu YouTube: ")
        threaded_chat_listener = multiprocessing.Process(target=start_chat_listener, args=(video_url, authors_set, stop_event_global))
        threaded_chat_listener.start()
        ask = input("Naciśnij Enter, aby zatrzymać zbieranie komentarzy...")
        stop_event_global.set()
        threaded_chat_listener.join()
        if not authors_set: 
            print("Nie zebrano żadnych komentarzy.")
        else:
            for index, author in enumerate(list(authors_set)):
                print(f"{index + 1}. {author}")
    print("Zbieranie komentarzy zostało zatrzymane.")
