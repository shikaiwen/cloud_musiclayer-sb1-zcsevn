from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import Base
from typing import List, Tuple


class MP3DownloadHistory(Base):
    __tablename__ = "mp3_download_history"

    id = Column(Integer, primary_key=True, index=True)
    create_time = Column(DateTime, default=datetime.utcnow)
    url = Column(String, index=True)
    download_cost_time = Column(Float)
    filename = Column(String)
    file_size = Column(Float)  # in MB
    status = Column(String)  # e.g., "completed", "failed"

    @classmethod
    def create(cls, db: Session, url: str, download_cost_time: float, filename: str, file_size: float, status: str):
        new_entry = cls(url=url, download_cost_time=download_cost_time, filename=filename, file_size=file_size, status=status)
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        return new_entry

    @classmethod
    def get_paginated(cls, db: Session, page: int = 1, per_page: int = 10) -> Tuple[List["MP3DownloadHistory"], int]:
        query = db.query(cls).order_by(cls.create_time.desc())
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        return items, total

    @classmethod
    def get_by_id(cls, db: Session, id: int):
        return db.query(cls).filter(cls.id == id).first()

    @classmethod
    def update(cls, db: Session, id: int, **kwargs):
        db.query(cls).filter(cls.id == id).update(kwargs)
        db.commit()
        return db.query(cls).filter(cls.id == id).first()

    @classmethod
    def delete(cls, db: Session, id: int):
        entry = db.query(cls).filter(cls.id == id).first()
        if entry:
            db.delete(entry)
            db.commit()
        return entry

    @classmethod
    def get_by_url(cls, db: Session, url: str):
        return db.query(cls).filter(cls.url == url).first()
