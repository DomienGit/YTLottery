import os
import uvicorn
from fastapi import FastAPI
from logic import AppManager

app = FastAPI()
app_manager: AppManager = None

@app.on_event("startup")
def startup_event():
    global app_manager
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
    
    app_manager.start_listener(video_url)
    queue_response = app_manager.from_listener_to_main_queue.get()  # Odbieramy odpowiedź z procesu nasłuchującego
    if not queue_response["success"]:
        return {
            "success": False,
            "message": queue_response["message"]}
    return {
        "success": True,
        "message": f"Video URL validated",
        "url": video_url}   

@app.post("/start")
def start_listener():
    app_manager.from_main_to_listener_queue.put({"status": "start"})  # Wysyłamy polecenie do procesu nasłuchującego
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

@app.post("/clear")
def clear_authors():
    app_manager.authors_manager.clear_authors()
    return {
        "success": True,
        "message": "All authors cleared"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
