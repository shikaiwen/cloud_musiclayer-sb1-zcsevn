from sqlalchemy.orm import Session
from app.repository.item_repository import ItemRepository
from app import schemas

class ItemService:
    @staticmethod
    def get_items(db: Session, skip: int = 0, limit: int = 100):
        return ItemRepository.get_items(db, skip=skip, limit=limit)

    @staticmethod
    def create_item(db: Session, item: schemas.ItemCreate):
        return ItemRepository.create_item(db, item)

    @staticmethod
    def get_item(db: Session, item_id: int):
        return ItemRepository.get_item(db, item_id)

    @staticmethod
    def update_item(db: Session, item_id: int, item: schemas.ItemCreate):
        return ItemRepository.update_item(db, item_id, item)

    @staticmethod
    def delete_item(db: Session, item_id: int):
        return ItemRepository.delete_item(db, item_id)