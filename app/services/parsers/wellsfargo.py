import re
from datetime import date
from .base import BaseParser


class WellsFargoParser(BaseParser):
    bank = "Wells Fargo"

    def parse(self, pdf_bytes: bytes) -> list[dict]:
        text = self.extract_full_text(pdf_bytes)
        year = self._extract_year(text)
        billing_end_month = self._extract_billing_end_month(text)
        return self._parse_transactions(text, year, billing_end_month)

    def _extract_year(self, text: str) -> int:
        # "Statement Period 02/04/2026 to 03/03/2026"
        m = re.search(r'Statement Period\s+\d{2}/\d{2}/(\d{4})', text)
        if m:
            return int(m.group(1))
        return date.today().year

    def _extract_billing_end_month(self, text: str) -> int:
        m = re.search(r'Statement Period.*?to\s+(\d{2})/\d{2}/\d{4}', text)
        if m:
            return int(m.group(1))
        return 12

    def _parse_transactions(self, text: str, year: int, billing_end_month: int) -> list[dict]:
        section_match = re.search(
            r'Purchases, Balance Transfers & Other Charges(.*?)(?:TOTAL PURCHASES|Fees Charged)',
            text, re.DOTALL
        )
        if not section_match:
            return []

        section = section_match.group(1)
        transactions = []

        # Pattern: CARD_LAST4  MM/DD  MM/DD  REF_NUM  DESCRIPTION  AMOUNT
        pattern = re.compile(
            r'\d{4}\s+(\d{2}/\d{2})\s+\d{2}/\d{2}\s+\S+\s+(.+?)\s+(\d{1,3}(?:,\d{3})*\.\d{2})\s*$',
            re.MULTILINE
        )

        for m in pattern.finditer(section):
            sale_date_str, description, amount_str = m.groups()
            amount = float(amount_str.replace(',', ''))
            month, day = map(int, sale_date_str.split('/'))
            txn_year = year if month <= billing_end_month else year - 1
            sale_date = date(txn_year, month, day)
            transactions.append({
                'sale_date': sale_date,
                'description': description.strip(),
                'amount': amount,
            })

        return transactions
