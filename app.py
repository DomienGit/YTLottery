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

def collect_comments(video_url, author_manager):
    video_id = get_video_id(video_url)
    if not video_id:
        print("Invalid YouTube URL")
        return

    chat = pytchat.create(video_id="3IAo_TUCWQA")
    while chat.is_alive():
        for c in chat.get().sync_items():
            print(f"{c.author.name}")
            author_manager.add_author(c.author.name)

def main(video_url):
    author_manager = CommentAuthors()
    collect_comments(video_url, author_manager)
        

if __name__ == "__main__":
    print("Starting to collect comments...")
    main("https://www.youtube.com/watch?v=3IAo_TUCWQA")
