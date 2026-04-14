from sqlalchemy.orm import Session
from app.models.pdf import PDFFile

def upload_pdf(db: Session, filename: str, content_type: str, data: bytes):
    pdf = PDFFile(
        filename=filename,
        content_type=content_type,
        size=len(data),
        data=data,
    )
    db.add(pdf)
    db.commit()
    db.refresh(pdf)
    return pdf

def get_pdfs(db: Session):
    return db.query(PDFFile).all()

def get_pdf_by_id(db: Session, pdf_id: int):
    return db.query(PDFFile).filter(PDFFile.id == pdf_id).first()
