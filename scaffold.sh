#!/bin/bash

# Create directory structure
mkdir -p app/api/v1/routes
mkdir -p app/core
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/services
mkdir -p app/db
mkdir -p tests

# Create __init__.py files
touch app/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/api/v1/routes/__init__.py
touch app/core/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py
touch app/db/__init__.py
touch tests/__init__.py

# Create main application files
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from app.api.v1.routes import items

app = FastAPI(title="Sample FastAPI", version="1.0.0")

app.include_router(items.router, prefix="/api/v1")
EOF

cat > app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Sample FastAPI"
    debug: bool = False
    database_url: str = "sqlite:///./dev.db"

    class Config:
        env_file = ".env"

settings = Settings()
EOF

cat > app/db/session.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF

cat > app/models/item.py << 'EOF'
from sqlalchemy import Column, Integer, String
from app.db.session import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
EOF

cat > app/schemas/item.py << 'EOF'
from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int

    class Config:
        from_attributes = True
EOF

cat > app/services/item.py << 'EOF'
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
EOF

cat > app/api/v1/routes/items.py << 'EOF'
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
EOF

cat > tests/test_items.py << 'EOF'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_items():
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
EOF

cat > .env.example << 'EOF'
APP_NAME=Sample FastAPI
DEBUG=false
DATABASE_URL=sqlite:///./dev.db
EOF

echo "Scaffolding complete!"
