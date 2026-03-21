from logic import get_video_id, create_chat_connection

url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
video_id = get_video_id(url)
print(f"Extracted Video ID: {video_id}")

chat = create_chat_connection(url)
if chat is not None:
    print("Chat connection established successfully.")
    print(f"Chat object: {video_id}")
else:    print("Failed to establish chat connection.")
