from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.pdf import PDFResponse
from app.services import pdf as pdf_service

router = APIRouter(prefix="/pdfs", tags=["pdfs"])

@router.post("/upload", response_model=PDFResponse)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    data = await file.read()
    return pdf_service.upload_pdf(db, file.filename, file.content_type, data)

@router.get("/", response_model=list[PDFResponse])
def list_pdfs(db: Session = Depends(get_db)):
    return pdf_service.get_pdfs(db)

@router.get("/{pdf_id}/download")
def download_pdf(pdf_id: int, db: Session = Depends(get_db)):
    pdf = pdf_service.get_pdf_by_id(db, pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    return Response(
        content=pdf.data,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={pdf.filename}"},
    )
