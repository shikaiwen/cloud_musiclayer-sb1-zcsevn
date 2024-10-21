from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app import schemas
from app.database import get_db
from app.service.item_service import ItemService
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

from app.mp3_download_history import MP3DownloadHistory
from app.youtube_downloader import DownloadRequest, MP3DownloadHistoryResponse, download_and_convert

router = APIRouter()

@router.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return ItemService.create_item(db=db, item=item)

@router.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = ItemService.get_items(db, skip=skip, limit=limit)
    return items

@router.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = ItemService.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = ItemService.update_item(db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.delete("/items/{item_id}", response_model=schemas.Item)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = ItemService.delete_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.post("/download")
async def download_video(request: DownloadRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
        # Check if the URL already exists in the download history
    existing_entry = MP3DownloadHistory.get_by_url(db, request.url)
    if existing_entry and existing_entry.status == "completed":
            return JSONResponse(content={"ok":False,"message": "file is already been downloaded", "history_id": existing_entry.id})

    history_id = await download_and_convert(request.url, db, background_tasks)
    return JSONResponse(content={"ok":True,"message": "Download started", "history_id": history_id}, status_code=202)

@router.get("/download-history")
def get_download_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items, total = MP3DownloadHistory.get_paginated(db, page=page, per_page=per_page)
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

@router.get("/download-history/{history_id}")
def get_download_history_by_id(history_id: int, db: Session = Depends(get_db)):
    history_item = MP3DownloadHistory.get_by_id(db, history_id)
    if history_item is None:
        raise HTTPException(status_code=404, detail="Download history not found")
    return history_item

@router.put("/download-history/{history_id}", response_model=MP3DownloadHistoryResponse)
def update_download_history(history_id: int, updated_data: dict, db: Session = Depends(get_db)):
    updated_item = MP3DownloadHistory.update(db, history_id, **updated_data)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Download history not found")
    return updated_item

@router.delete("/download-history/{history_id}")
def delete_download_history(history_id: int, db: Session = Depends(get_db)):
    deleted_item = MP3DownloadHistory.delete(db, history_id)
    if deleted_item is None:
        raise HTTPException(status_code=404, detail="Download history not found")
    return JSONResponse(content={"message": "Download history deleted successfully"}, status_code=200)

@router.get("/mp3/{filename}")
async def get_mp3(filename: str):
    mp3_folder = ""  # Adjust this path to where your MP3 files are stored
    file_path = os.path.join(mp3_folder, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="MP3 file not found")
    
    return FileResponse(file_path, media_type="audio/mpeg", filename=filename)

@router.get("/", response_class=HTMLResponse)
async def read_root():
    with open("app/static/index.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)