import yt_dlp
import os
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from app.mp3_download_history import MP3DownloadHistory
from app.database import SessionLocal, engine
import time
from typing import List

app = FastAPI()

class DownloadRequest(BaseModel):
    url: str

class MP3DownloadHistoryResponse(BaseModel):
    id: int
    create_time: datetime
    url: str
    download_cost_time: float
    filename: str
    file_size: float
    status: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def download_progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} of {d['_total_bytes_str']} at {d['_speed_str']}")
    elif d['status'] == 'finished':
        print("Download completed. Converting to MP3...")

async def download_and_convert(url: str, db: Session, background_tasks: BackgroundTasks):
    start_time = time.time()
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'progress_hooks': [download_progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            filename = ydl.prepare_filename(info)
            mp3_filename = os.path.splitext(filename)[0] + '.mp3'
        
        # Create a new download history entry with "pending" status
        history_entry = MP3DownloadHistory.create(
            db=db,
            url=url,
            download_cost_time=0,
            filename=mp3_filename,
            file_size=0,
            status="pending"
        )

        # Start the download process asynchronously
        background_tasks.add_task(perform_download, url, ydl_opts, db, history_entry.id, start_time)

        return history_entry.id
    except Exception as e:
        end_time = time.time()
        download_cost_time = end_time - start_time

        history_entry = MP3DownloadHistory.create(
            db=db,
            url=url,
            download_cost_time=download_cost_time,
            filename="",
            file_size=0,
            status="failed"
        )

        raise e

async def perform_download(url: str, ydl_opts: dict, db: Session, history_id: int, start_time: float):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            mp3_filename = os.path.splitext(filename)[0] + '.mp3'
        
        end_time = time.time()
        download_cost_time = end_time - start_time
        file_size = os.path.getsize(mp3_filename) / (1024 * 1024)  # Convert to MB

        MP3DownloadHistory.update(
            db=db,
            id=history_id,
            download_cost_time=download_cost_time,
            filename=mp3_filename,
            file_size=file_size,
            status="completed"
        )
    except Exception as e:
        end_time = time.time()
        download_cost_time = end_time - start_time

        MP3DownloadHistory.update(
            db=db,
            id=history_id,
            download_cost_time=download_cost_time,
            filename="",
            file_size=0,
            status="failed"
        )

        print(f"Error during download: {str(e)}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("youtube_downloader:app", host="0.0.0.0", port=8001, reload=True)