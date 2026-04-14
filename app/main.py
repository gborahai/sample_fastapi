from fastapi import FastAPI
from app.api.v1.routes import items, pdfs
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sample FastAPI", version="1.0.0")

app.include_router(items.router, prefix="/api/v1")
app.include_router(pdfs.router, prefix="/api/v1")
