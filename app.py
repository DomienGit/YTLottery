import uvicorn
from fastapi import FastAPI
from logic import AppManager
from logic import validate_video_url, start_chat_listener

app = FastAPI()
app_manager = AppManager()

@app.get("/")
def read_root():
    return {
        "success": True,
        "message": "welcome to the YouTube Chat Listener"}

@app.get("/authors")
def get_authors():
    return {
        "success": True,
        "message": list(app_manager.authors_manager.get_authors())}

@app.post("/apply-url/{video_url}")
def apply_url(video_url: str):
    if not video_url:
        return {
            "success": False,
            "message": "Type a video URL"}
    if not validate_video_url(video_url):
        return {
            "success": False,
            "message": "Invalid video URL"}   
    return {
        "success": True,
        "message": f"Video URL validated",
        "url": video_url}   

@app.post("/start/{video_url}")
def start_listener(video_url: str):
    app_manager.start_listener(video_url)
    return {
        "success": True,
        "message": "Chat listener started"}

@app.post("/stop")
def stop_listener():
    app_manager.stop_listener()
    return {
        "success": True,
        "message": "Chat listener stopped"}

@app.post("/draw")
def draw_winner():
    winner = app_manager.authors_manager.draw_winner()
    if winner is None:
        return {
            "success": False,
            "message": "No authors to draw from"}
    return {
        "success": True,
        "message": "Winner drawn",
        "winner": winner}

@app.post("/delete/{author_name}")
def delete_author(author_name: str):
    app_manager.authors_manager.delete_author(author_name)
    return {
        "success": True,
        "message": f"Author '{author_name}' deleted"}


