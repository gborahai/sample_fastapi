from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.pdf import PDFResponse, PDFUploadResponse
from app.services import pdf as pdf_service
from app.services import analyser

router = APIRouter(prefix="/pdfs", tags=["pdfs"])


@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    data = await file.read()
    pdf = pdf_service.upload_pdf(db, file.filename, file.content_type, data)

    # Auto-parse transactions after upload
    try:
        transactions = analyser.parse_and_store(db, pdf.id)
        bank = transactions[0].bank if transactions else None
        transactions_parsed = len(transactions)
    except ValueError:
        # Unsupported bank — upload still succeeds, parse manually later
        bank = None
        transactions_parsed = 0

    return PDFUploadResponse(
        id=pdf.id,
        filename=pdf.filename,
        content_type=pdf.content_type,
        size=pdf.size,
        uploaded_at=pdf.uploaded_at,
        transactions_parsed=transactions_parsed,
        bank=bank,
    )

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
