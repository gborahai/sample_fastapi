from pydantic import BaseModel
from datetime import datetime

class PDFResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
