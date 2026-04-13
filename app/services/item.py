from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate

def get_items(db: Session):
    return db.query(Item).all()

def create_item(db: Session, item: ItemCreate):
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
