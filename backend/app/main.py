# python modules
import os

# third-party modules
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from yt_dlp import YoutubeDL

app = FastAPI()

# Allow CORS so the Chrome extension can make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
