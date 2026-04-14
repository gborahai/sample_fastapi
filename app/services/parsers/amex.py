import re
from datetime import date
from .base import BaseParser


class AmexParser(BaseParser):
    bank = "Amex"

    STOP_MARKERS = ["Fees", "Total Fees", "Interest Charged", "About Trailing"]

    def parse(self, pdf_bytes: bytes) -> list[dict]:
        text = self.extract_full_text(pdf_bytes)
        section = self._extract_charges_section(text)
        return self._parse_section(section)

    def _extract_charges_section(self, text: str) -> str:
        # Find "New Charges" section start
        nc_match = re.search(r'New Charges', text)
        if not nc_match:
            return ""
        remaining = text[nc_match.start():]

        # Find first "Fees" section that ends the charges
        fees_match = re.search(r'\nFees\s*\nAmount', remaining)
        if fees_match:
            return remaining[:fees_match.start()]
        return remaining

    def _parse_section(self, text: str) -> list[dict]:
        transactions = []
        date_re = re.compile(r'^(\d{2}/\d{2}/\d{2})\s+(.*)')
        amount_re = re.compile(r'\$([0-9,]+\.\d{2})')
        phone_re = re.compile(r'[\+]?\d[\d\-\(\)\s]{9,}')

        lines = [l.strip() for l in text.split('\n')]
        i = 0

        while i < len(lines):
            line = lines[i]
            if not line or any(m.lower() in line.lower() for m in self.STOP_MARKERS):
                i += 1
                continue

            m = date_re.match(line)
            if m:
                date_str = m.group(1)
                txn_text = m.group(2).strip()

                # Collect continuation lines until next date or stop marker
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    if date_re.match(next_line):
                        break
                    if any(marker.lower() in next_line.lower() for marker in self.STOP_MARKERS):
                        break
                    txn_text += ' ' + next_line
                    j += 1
                i = j

                # Extract amount (last dollar value in the collected text)
                amounts = amount_re.findall(txn_text)
                if amounts:
                    amount = float(amounts[-1].replace(',', ''))
                    # Clean description: remove amount, phone numbers
                    description = amount_re.sub('', txn_text)
                    description = phone_re.sub('', description)
                    description = re.sub(r'\s+', ' ', description).strip()

                    mo, day, yr = date_str.split('/')
                    sale_date = date(2000 + int(yr), int(mo), int(day))
                    transactions.append({
                        'sale_date': sale_date,
                        'description': description,
                        'amount': amount,
                    })
                continue

            i += 1

        return transactions
