# python modules
import os
import sys
import logging
import time

# third-party modules
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from yt_dlp import YoutubeDL
from uvicorn import Config, Server

log_file = os.path.join(os.path.expanduser("~"), "DownloadService.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

sys.stdout = open(log_file, "a")
sys.stderr = open(log_file, "a")

logging.info("Starting DownloadService...")

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

def update_file_timestamp(file_path):
    current_time = time.time()
    os.utime(file_path, (current_time, current_time))

@app.post("/download")
def download_video(request: VideoRequest):
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

    base_dir = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
    
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
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        },
        'ffmpeg_location': os.path.join(base_dir, 'bin'),
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(request.url, download=True)
            file_path = os.path.join(downloads_folder, f"{info['title']}.{info['ext']}")
            update_file_timestamp(file_path)

        logging.info(f"Video downloaded: {request.url}")
        return {"message": "Download completed", "location": downloads_folder}
    except Exception as e:
        logging.error(f"Error downloading video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")

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