from io import BytesIO
import pdfplumber
from .base import BaseParser
from .citi import CitiParser
from .amex import AmexParser
from .wellsfargo import WellsFargoParser


def detect_bank(pdf_bytes: bytes) -> str:
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        first_page = pdf.pages[0].extract_text() or ""

    text = first_page.upper()
    if "AMERICAN EXPRESS" in text:
        return "amex"
    if "WELLS FARGO" in text:
        return "wellsfargo"
    if "CITI" in text:
        return "citi"
    return "unknown"


def get_parser(pdf_bytes: bytes) -> BaseParser:
    bank = detect_bank(pdf_bytes)
    parsers = {
        "citi": CitiParser(),
        "amex": AmexParser(),
        "wellsfargo": WellsFargoParser(),
    }
    parser = parsers.get(bank)
    if not parser:
        raise ValueError(
            f"Unsupported bank detected: '{bank}'. Supported: {list(parsers.keys())}"
        )
    return parser
