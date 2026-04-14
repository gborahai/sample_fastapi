from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.transaction import (
    AnalysisResponse,
    BankSummary,
    CategorySummary,
    MonthlyReportResponse,
    MonthSummary,
    TransactionResponse,
)
from app.services import analyser

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/{pdf_id}/parse", response_model=list[TransactionResponse])
def parse_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """Parse a PDF statement and store its transactions in the DB."""
    try:
        transactions = analyser.parse_and_store(db, pdf_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not transactions:
        raise HTTPException(status_code=404, detail="PDF not found or no transactions extracted")
    return transactions


@router.get("/{pdf_id}", response_model=AnalysisResponse)
def get_analysis(pdf_id: int, db: Session = Depends(get_db)):
    """Return calendar month-wise expense analysis for a parsed PDF."""
    result = analyser.get_monthly_analysis(db, pdf_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail="No transactions found. Call POST /analysis/{pdf_id}/parse first.",
        )

    months = {}
    for month_key, data in result["months"].items():
        months[month_key] = MonthSummary(
            month=month_key,
            total=round(data["total"], 2),
            by_category={
                cat: CategorySummary(total=round(v["total"], 2), count=v["count"])
                for cat, v in data["by_category"].items()
            },
            transactions=data["transactions"],
        )

    return AnalysisResponse(pdf_id=result["pdf_id"], bank=result["bank"], months=months)


@router.get("/report/{year}/{month}", response_model=MonthlyReportResponse)
def get_monthly_report(year: int, month: int, db: Session = Depends(get_db)):
    """Return a cross-bank expense report for a specific calendar month (e.g. /report/2026/2)."""
    if not (1 <= month <= 12):
        raise HTTPException(status_code=422, detail="Month must be between 1 and 12")

    result = analyser.get_monthly_report(db, year, month)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"No transactions found for {year}-{month:02d}. Make sure PDFs are parsed first.",
        )

    by_bank = {
        bank_name: BankSummary(
            bank=bank_name,
            total=round(data["total"], 2),
            by_category={
                cat: CategorySummary(total=round(v["total"], 2), count=v["count"])
                for cat, v in data["by_category"].items()
            },
            transactions=data["transactions"],
        )
        for bank_name, data in result["by_bank"].items()
    }

    by_category = {
        cat: CategorySummary(total=round(v["total"], 2), count=v["count"])
        for cat, v in result["by_category"].items()
    }

    return MonthlyReportResponse(
        month=result["month"],
        grand_total=result["grand_total"],
        by_bank=by_bank,
        by_category=by_category,
        transactions=result["transactions"],
    )
