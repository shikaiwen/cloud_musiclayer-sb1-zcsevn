from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from datetime import datetime
# Base = declarative_base()
from app.database import Base


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
    def get_all(cls, db: Session, skip: int = 0, limit: int = 100):
        return db.query(cls).offset(skip).limit(limit).all()

    @classmethod
    def get_by_id(cls, db: Session, entry_id: int):
        return db.query(cls).filter(cls.id == entry_id).first()

    @classmethod
    def update(cls, db: Session, entry_id: int, **kwargs):
        db.query(cls).filter(cls.id == entry_id).update(kwargs)
        db.commit()
        return db.query(cls).filter(cls.id == entry_id).first()

    @classmethod
    def delete(cls, db: Session, entry_id: int):
        entry = db.query(cls).filter(cls.id == entry_id).first()
        if entry:
            db.delete(entry)
            db.commit()
        return entry

# Don't forget to create the table in your database
# You can do this by running the following code when setting up your database:
# Base.metadata.create_all(bind=engine)