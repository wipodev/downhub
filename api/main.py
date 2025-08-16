# python modules
import os
import sys
import logging
import time
import traceback
import threading
import uuid

# third-party modules
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from yt_dlp import YoutubeDL
from uvicorn import Config, Server

# --- Logging config ---
log_file = os.path.join(os.path.expanduser("~"), "DownHubService.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

sys.stdout = open(log_file, "a")
sys.stderr = open(log_file, "a")

logging.info("Starting DownHubService...")

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://mppaemmnjblpfpiijkbmgfbkmkgjlean",
        "http://127.0.0.1",
        "http://localhost"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

tasks = {}  # {task_id: {"status": "pending"|"completed"|"error", "file": str|None, "error_msg": str|None}}

def download_job(task_id, url):
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    base_dir = os.path.dirname(
        os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)
    )

    ydl_opts = {
        'outtmpl': os.path.join(downloads_folder, '%(title)s.%(ext)s'),
        "restrictfilenames": True,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        "merge_output_format": "mp4",
        "hls_prefer_native": True,
        "continuedl": True,
        "fragment_retries": 10,
        "retries": 5,
        "concurrent_fragment_downloads": 5,
        "quiet": True,
        "noprogress": True,
        "no_mtime": True,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        },
        'ffmpeg_location': os.path.join(base_dir, 'bin'),
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = os.path.join(downloads_folder, f"{info['title']}.{info['ext']}")

        tasks[task_id]["status"] = "completed"
        tasks[task_id]["file"] = file_path
        logging.info(f"Download completed for task {task_id}")
    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error_msg"] = str(e)
        logging.error(f"Error in task {task_id}: {e}")
        logging.error(traceback.format_exc())

@app.post("/download")
def start_download(request: VideoRequest):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "file": None, "error_msg": None}

    threading.Thread(target=download_job, args=(task_id, request.url), daemon=True).start()

    logging.info(f"Download started for {request.url} as task {task_id}")
    return {"message": "Download started in background", "task_id": task_id}

@app.get("/status/{task_id}")
def get_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

if __name__ == "__main__":
    logger = logging.getLogger("uvicorn")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    config = Config(app=app, host="127.0.0.1", port=8000, log_level="info", use_colors=False)
    server = Server(config)

    logging.info("Starting server...")
    server.run()
