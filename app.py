import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse  # Dodaj to
from logic import AppManager
from pydantic import BaseModel

class VideoURL(BaseModel):
    url: str

class AuthorRequest(BaseModel):
    name: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app_manager: AppManager = None

@app.on_event("startup")
def startup_event():
    global app_manager
    app_manager = AppManager()

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/style.css")
def get_style():
    return FileResponse("style.css")

@app.get("/script.js")
def get_script():
    return FileResponse("script.js")

@app.get("/authors")
def get_authors():
    return {
        "success": True,
        "message": list(app_manager.authors_manager.get_authors())}

@app.post("/apply-url")
def apply_url(data: VideoURL):
    video_url = data.url
    if not video_url:
        return {
            "success": False,
            "message": "Type a video URL"}
    
    app_manager.start_listener(video_url)
    queue_response = app_manager.from_listener_to_main_queue.get()
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
    app_manager.from_main_to_listener_queue.put({"status": "start"})
    return {
        "success": True,
        "message": "Chat listener started"}

@app.post("/stop")
def stop_listener():
    app_manager.stop_fetching_authors()
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

@app.post("/delete")
def delete_author(data: AuthorRequest):
    app_manager.authors_manager.delete_author(data.name)
    return {
        "success": True,
        "message": f"Author '{data.name}' deleted"}

@app.post("/add-author")
def add_author(data: AuthorRequest):
    app_manager.authors_manager.add_author(data.name)
    return {
        "success": True,
        "message": f"Author '{data.name}' added"}

@app.post("/clear")
def clear_authors(data: dict = None): # Dodano dict, aby przyjąć {} z frontendu
    app_manager.authors_manager.clear_authors()
    return {
        "success": True,
        "message": "All authors cleared"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
