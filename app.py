import pytchat
import re

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

def main(video_url):
    video_id = get_video_id(video_url)
    if not video_id:
        print("Invalid YouTube URL")
        return

    chat = pytchat.create(video_id=video_id)
    while chat.is_alive():
        for c in chat.get().sync_items():
            print(f"{c.datetime} [{c.author.name}]- {c.message}")

if __name__ == "__main__":
    print("Starting to collect comments...")
    main("https://www.youtube.com/watch?v=ft0oRojsZAA")
