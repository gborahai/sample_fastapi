import re
from datetime import date
from .base import BaseParser


class CitiParser(BaseParser):
    bank = "Citi"

    def parse(self, pdf_bytes: bytes) -> list[dict]:
        text = self.extract_full_text(pdf_bytes)
        year = self._extract_year(text)
        billing_end_month = self._extract_billing_end_month(text)
        return self._parse_transactions(text, year, billing_end_month)

    def _extract_year(self, text: str) -> int:
        # "Billing Period: 01/21/26-02/19/26" → 2026
        m = re.search(r'Billing Period:\s*\d{2}/\d{2}/\d{2}-\d{2}/\d{2}/(\d{2})', text)
        if m:
            return 2000 + int(m.group(1))
        return date.today().year

    def _extract_billing_end_month(self, text: str) -> int:
        m = re.search(r'Billing Period:\s*\d{2}/\d{2}/\d{2}-(\d{2})/\d{2}/\d{2}', text)
        if m:
            return int(m.group(1))
        return 12

    def _parse_transactions(self, text: str, year: int, billing_end_month: int) -> list[dict]:
        # Extract section between "Standard Purchases" and "Fees Charged"
        section_match = re.search(
            r'Standard Purchases(.*?)(?:Fees Charged|TOTAL FEES)',
            text, re.DOTALL
        )
        if not section_match:
            return []

        section = section_match.group(1)
        transactions = []

        # Pattern: MM/DD  MM/DD  DESCRIPTION  $AMOUNT
        pattern = re.compile(
            r'(\d{2}/\d{2})\s+(\d{2}/\d{2})\s+(.+?)\s+\$([0-9,]+\.\d{2})',
            re.MULTILINE
        )

        for m in pattern.finditer(section):
            sale_date_str, _, description, amount_str = m.groups()
            amount = float(amount_str.replace(',', ''))
            month, day = map(int, sale_date_str.split('/'))
            # Transactions with month > billing end month belong to the previous year
            txn_year = year if month <= billing_end_month else year - 1
            sale_date = date(txn_year, month, day)
            transactions.append({
                'sale_date': sale_date,
                'description': description.strip(),
                'amount': amount,
            })

        return transactions
