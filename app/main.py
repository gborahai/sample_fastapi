from fastapi import FastAPI
from app.api.v1.routes import items

app = FastAPI(title="Sample FastAPI", version="1.0.0")

app.include_router(items.router, prefix="/api/v1")
