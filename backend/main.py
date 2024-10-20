from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import yt_dlp
import os
from app.api import router
from app.database import engine, Base

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Create database tables
Base.metadata.create_all(bind=engine)

# Create audios directory if it doesn't exist
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audios")
os.makedirs(AUDIO_DIR, exist_ok=True)

class DownloadRequest(BaseModel):
    url: str

def download_progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']}")
    elif d['status'] == 'finished':
        print("Download completed. Converting to MP3...")

def download_and_convert(url: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(AUDIO_DIR, '%(title)s.%(ext)s'),
        'progress_hooks': [download_progress_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        mp3_filename = os.path.splitext(filename)[0] + '.mp3'
    
    return mp3_filename

@app.post("/download")
async def download_video(request: DownloadRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(download_and_convert, request.url)
    return JSONResponse(content={"message": "Download started"}, status_code=202)

@app.get("/hello")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)