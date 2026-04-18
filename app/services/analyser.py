from collections import defaultdict
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.models.transaction import Transaction
from app.models.pdf import PDFFile
from app.services.parsers.factory import get_parser
from app.services.categorizer import categorize


def parse_and_store(db: Session, pdf_id: int) -> list[Transaction]:
    pdf = db.query(PDFFile).filter(PDFFile.id == pdf_id).first()
    if not pdf:
        return []

    # Clear existing transactions for this PDF before re-parsing
    db.query(Transaction).filter(Transaction.pdf_id == pdf_id).delete()
    db.commit()

    parser = get_parser(pdf.data)
    raw = parser.parse(pdf.data)

    transactions = []
    for t in raw:
        txn = Transaction(
            pdf_id=pdf_id,
            bank=parser.bank,
            sale_date=t["sale_date"],
            description=t["description"],
            amount=t["amount"],
            category=categorize(t["description"]),
        )
        db.add(txn)
        transactions.append(txn)

    db.commit()
    for txn in transactions:
        db.refresh(txn)

    return transactions


def get_monthly_analysis(db: Session, pdf_id: int) -> dict:
    transactions = (
        db.query(Transaction)
        .filter(Transaction.pdf_id == pdf_id)
        .order_by(Transaction.sale_date)
        .all()
    )
    if not transactions:
        return {}

    months: dict = defaultdict(lambda: {
        "total": 0.0,
        "by_category": defaultdict(lambda: {"total": 0.0, "count": 0}),
        "transactions": [],
    })

    for txn in transactions:
        key = txn.sale_date.strftime("%Y-%m")
        months[key]["total"] += txn.amount
        months[key]["by_category"][txn.category]["total"] += txn.amount
        months[key]["by_category"][txn.category]["count"] += 1
        months[key]["transactions"].append(txn)

    return {
        "pdf_id": pdf_id,
        "bank": transactions[0].bank,
        "months": dict(sorted(months.items())),
    }


def get_monthly_category_report(db: Session, year: int, month: int, category: str) -> dict:
    """Aggregate transactions for a specific category across all banks for a given calendar month."""
    transactions = (
        db.query(Transaction)
        .filter(
            extract("year", Transaction.sale_date) == year,
            extract("month", Transaction.sale_date) == month,
            Transaction.category == category,
        )
        .order_by(Transaction.sale_date)
        .all()
    )
    if not transactions:
        return {}

    month_key = date(year, month, 1).strftime("%Y-%m")
    grand_total = 0.0
    by_bank: dict = defaultdict(lambda: {"total": 0.0, "count": 0, "transactions": []})

    for txn in transactions:
        grand_total += txn.amount
        by_bank[txn.bank]["total"] += txn.amount
        by_bank[txn.bank]["count"] += 1
        by_bank[txn.bank]["transactions"].append(txn)

    return {
        "month": month_key,
        "category": category,
        "grand_total": round(grand_total, 2),
        "count": len(transactions),
        "by_bank": {k: {"total": round(v["total"], 2), "count": v["count"], "transactions": v["transactions"]} for k, v in by_bank.items()},
        "transactions": transactions,
    }


def get_monthly_report(db: Session, year: int, month: int) -> dict:
    """Aggregate all transactions across all banks for a given calendar month."""
    transactions = (
        db.query(Transaction)
        .filter(
            extract("year", Transaction.sale_date) == year,
            extract("month", Transaction.sale_date) == month,
        )
        .order_by(Transaction.sale_date)
        .all()
    )
    if not transactions:
        return {}

    month_key = date(year, month, 1).strftime("%Y-%m")
    grand_total = 0.0
    by_bank: dict = defaultdict(lambda: {
        "total": 0.0,
        "by_category": defaultdict(lambda: {"total": 0.0, "count": 0}),
        "transactions": [],
    })
    by_category: dict = defaultdict(lambda: {"total": 0.0, "count": 0})

    for txn in transactions:
        grand_total += txn.amount
        by_bank[txn.bank]["total"] += txn.amount
        by_bank[txn.bank]["by_category"][txn.category]["total"] += txn.amount
        by_bank[txn.bank]["by_category"][txn.category]["count"] += 1
        by_bank[txn.bank]["transactions"].append(txn)
        by_category[txn.category]["total"] += txn.amount
        by_category[txn.category]["count"] += 1

    # Attach bank name to each bank summary
    for bank_name, data in by_bank.items():
        data["bank"] = bank_name

    return {
        "month": month_key,
        "grand_total": round(grand_total, 2),
        "by_bank": dict(by_bank),
        "by_category": dict(by_category),
        "transactions": transactions,
    }
