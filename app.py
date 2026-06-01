from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from logic import AppManager
from pydantic import BaseModel, Field
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoURL(BaseModel):
    url: str

class AuthorRequest(BaseModel):
    name: str

class KeywordRequest(BaseModel):
    keyword: str = Field(default="")

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

app = FastAPI()

app.mount("/img", StaticFiles(directory="img"), name="img")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app_manager: AppManager = None
ws_manager = ConnectionManager()

def get_app_manager():
    return app_manager

async def broadcast_authors():
    """Broadcast current authors list to all WebSocket clients."""
    if app_manager:
        authors = list(app_manager.authors_manager.get_authors().values())
        await ws_manager.broadcast({"type": "authors_update", "authors": authors})

def sync_broadcast_authors():
    """Schedule broadcast from sync context (REST endpoints)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(broadcast_authors())
    except RuntimeError:
        pass

async def listen_for_notifications():
    """Background task: read from multiprocessing queue and broadcast via WebSocket."""
    while True:
        try:
            notification = await asyncio.get_event_loop().run_in_executor(
                None, app_manager.author_notification_queue.get
            )
            await ws_manager.broadcast(notification)
        except Exception as e:
            logger.error(f"Notification listener error: {e}")
            await asyncio.sleep(0.5)

@app.on_event("startup")
async def startup_event():
    global app_manager
    app_manager = AppManager()
    asyncio.create_task(listen_for_notifications())

@app.on_event("shutdown")
def shutdown_event():
    if app_manager:
        app_manager.terminate_process()
    else:
        pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial state
        if app_manager:
            authors = list(app_manager.authors_manager.get_authors().values())
            await websocket.send_json({"type": "authors_update", "authors": authors})
        # Keep connection alive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

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
def get_authors(app_manager: AppManager = Depends(get_app_manager)):
    return {
        "success": True,
        "message": list(app_manager.authors_manager.get_authors().values())
        }

@app.post("/apply-url")
def apply_url(data: VideoURL, app_manager: AppManager = Depends(get_app_manager)):
    video_url = data.url
    if not video_url:
        return {
            "success": False,
            "message": "Type a video URL"}

    app_manager.start_chat_fetching_process(video_url)
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
def start_listener(data: KeywordRequest, app_manager: AppManager = Depends(get_app_manager)):
    keyword = data.keyword
    app_manager.from_main_to_listener_queue.put({"status": "start", "keyword": keyword})
    return {
        "success": True,
        "message": "Chat listener started"}

@app.post("/stop")
def stop_listener(app_manager: AppManager = Depends(get_app_manager)):
    app_manager.stop_fetching_authors()
    return {
        "success": True,
        "message": "Chat listener stopped"}

@app.post("/draw")
def draw_winner(app_manager: AppManager = Depends(get_app_manager)):
    winner = app_manager.authors_manager.draw_winner()
    if winner is None:
        return {
            "success": False,
            "message": "No authors to draw from"}
    return {
        "success": True,
        "message": "Winner drawn",
        "winner": winner["author"],
        "img": winner["img"]
        }

@app.post("/delete")
def delete_author(data: AuthorRequest, app_manager: AppManager = Depends(get_app_manager)):
    app_manager.authors_manager.delete_author(data.name)
    sync_broadcast_authors()
    return {
        "success": True,
        "message": f"Author '{data.name}' deleted"}

@app.post("/add-author")
def add_author(data: AuthorRequest, app_manager: AppManager = Depends(get_app_manager)):
    app_manager.authors_manager.add_author(data.name)
    sync_broadcast_authors()
    return {
        "success": True,
        "message": f"Author '{data.name}' added"}

@app.post("/clear")
def clear_authors(app_manager: AppManager = Depends(get_app_manager)):
    app_manager.authors_manager.clear_authors()
    sync_broadcast_authors()
    return {
        "success": True,
        "message": "All authors cleared"}