from abc import ABC, abstractmethod
from io import BytesIO
import pdfplumber


class BaseParser(ABC):
    bank: str = ""

    def open_pdf(self, pdf_bytes: bytes):
        return pdfplumber.open(BytesIO(pdf_bytes))

    def extract_full_text(self, pdf_bytes: bytes) -> str:
        with self.open_pdf(pdf_bytes) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    @abstractmethod
    def parse(self, pdf_bytes: bytes) -> list[dict]:
        """Return list of dicts with keys: sale_date (date), description (str), amount (float)"""
        pass
