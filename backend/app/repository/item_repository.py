from sqlalchemy.orm import Session
from app import models, schemas

class ItemRepository:
    @staticmethod
    def get_items(db: Session, skip: int = 0, limit: int = 100):
        return db.query(models.Item).offset(skip).limit(limit).all()

    @staticmethod
    def create_item(db: Session, item: schemas.ItemCreate):
        db_item = models.Item(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def get_item(db: Session, item_id: int):
        return db.query(models.Item).filter(models.Item.id == item_id).first()

    @staticmethod
    def update_item(db: Session, item_id: int, item: schemas.ItemCreate):
        db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
        if db_item:
            for key, value in item.dict().items():
                setattr(db_item, key, value)
            db.commit()
            db.refresh(db_item)
        return db_item

    @staticmethod
    def delete_item(db: Session, item_id: int):
        db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
        if db_item:
            db.delete(db_item)
            db.commit()
        return db_item