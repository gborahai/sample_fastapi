from pydantic import BaseModel
from datetime import date


class TransactionResponse(BaseModel):
    id: int
    pdf_id: int
    bank: str
    sale_date: date
    description: str
    amount: float
    category: str

    class Config:
        from_attributes = True


class CategorySummary(BaseModel):
    total: float
    count: int


class MonthSummary(BaseModel):
    month: str
    total: float
    by_category: dict[str, CategorySummary]
    transactions: list[TransactionResponse]


class AnalysisResponse(BaseModel):
    pdf_id: int
    bank: str
    months: dict[str, MonthSummary]


class BankSummary(BaseModel):
    bank: str
    total: float
    by_category: dict[str, CategorySummary]
    transactions: list[TransactionResponse]


class MonthlyReportResponse(BaseModel):
    month: str          # e.g. "2026-02"
    grand_total: float
    by_bank: dict[str, BankSummary]
    by_category: dict[str, CategorySummary]
    transactions: list[TransactionResponse]
