import multiprocessing
import pytchat
import time
import re

stop_event = multiprocessing.Event()

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

def start_chat_listener(video_url):
    video_id = _get_video_id(video_url)
    if not video_id:
        print("Nieprawidłowy link do filmu.")
        return

    chat = pytchat.create(video_id=video_id)
    while not stop_event.is_set() and chat.is_alive():
        for c in chat.get().sync_items():
            print(c.author.name)


if __name__ == "__main__":
    video_url = input("Podaj link do filmu YouTube: ")
    threaded_chat_listener = multiprocessing.Process(target=start_chat_listener, args=(video_url,))
    threaded_chat_listener.start()
    ask = input("Naciśnij Enter, aby zatrzymać zbieranie komentarzy...")
    stop_event.set()
    threaded_chat_listener.join()
    print("Zbieranie komentarzy zostało zatrzymane.")
