# python modules
import os
import sys

# third-party modules
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from yt_dlp import YoutubeDL
import logging
from uvicorn import Config, Server

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

app = FastAPI()

class VideoRequest(BaseModel):
    url: str

@app.post("/download")
def download_video(request: VideoRequest):
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    
    ydl_opts = {
        'outtmpl': os.path.join(downloads_folder, '%(title)s.%(ext)s'),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([request.url])
        return {"message": "Download completed", "location": downloads_folder}
    except Exception as e:
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

    server.run()