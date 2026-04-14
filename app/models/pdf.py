from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class PDFFile(Base):
    __tablename__ = "pdf_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content_type = Column(String)
    size = Column(Integer)
    data = Column(LargeBinary)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
