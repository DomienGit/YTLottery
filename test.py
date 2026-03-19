import pytchat
import re
import sys

def get_video_id(url):
    """Returns the input URL as video ID, bypassing strict validation."""
    return url

def main():
    print("YouTube Live Chat Viewer")
    print("------------------------")

    while True:
        youtube_url = input("Please enter a YouTube live stream URL (or 'q' to quit): ")
        if youtube_url.lower() == 'q':
            print("Exiting.")
            sys.exit(0)

        video_id = get_video_id(youtube_url)

        if not video_id:
            print("Invalid YouTube URL. Please try again.")
            continue

        print(f"Connecting to live chat for video ID: {video_id}...")

        try:
            livechat = pytchat.create(video_id=video_id)
            print("Connected. Waiting for messages...")
            while livechat.is_alive():
                for c in livechat.get().sync_items():
                    print(f"[{c.datetime}] {c.author.name}: {c.message}")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please ensure the URL is for a live stream and the video ID is correct.")
        finally:
            print("Disconnected from live chat.")

if __name__ == "__main__":
    main()
