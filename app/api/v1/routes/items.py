from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.item import ItemCreate, ItemResponse
from app.services import item as item_service

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=list[ItemResponse])
def list_items(db: Session = Depends(get_db)):
    return item_service.get_items(db)

@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return item_service.create_item(db, item)
