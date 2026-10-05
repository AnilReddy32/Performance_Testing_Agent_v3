import csv
import io
import json
from pathlib import Path

from pypdf import PdfReader

MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10mb
MAX_ATTACHMENTS_PER_ISSUE = 5
MAX_EXTRACTED_CHARS = 100_000


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".json",
    ".csv",
    ".pdf",
}

def _limit_text(text: str) -> str:
    """
    Prevent extremely large attachment content from being sent to LLM
    """

    if len(text) <= MAX_EXTRACTED_CHARS:
        return text

    return (
        text[:MAX_EXTRACTED_CHARS] + "\n\n[Attachment content truncated due to size limit.]"
    )


def extract_txt(content: bytes) -> str:
    return _limit_text(
        content.decode("utf-8-sig", errors="replace")
    )

def extract_json(content: bytes) -> str:
    text = content.decode("utf-8-sig")

    data = json.loads(text)

    formatted = json.dumps(
        data,
        indent=2,
        ensure_ascii=False
    )

    return _limit_text(formatted)


def extract_csv(content: bytes) -> str:
    text = content.decode("utf-8-sig", errors="replace")

    reader = csv.reader(io.StringIO(text))

    rows = []

    for row in reader:
        rows.append(" | ".join(row))

    return _limit_text("\n".join(rows))

def extract_pdf(content: bytes) -> str:
    if not content.startswith(b"%PDF"):
        raise ValueError("File does not appear to be a valid PDF.")

    reader = PdfReader(io.BytesIO(content))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        if page_text.strip():
            pages.append(
                f"--- Page {page_number} --- \n"
                f"{page_text}"
            )

    return _limit_text("\n\n".join(pages))


def extract_attachment(filename: str, content: bytes) -> str:
    """
    Extract text from the supported documents
    """

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported attachment type: {extension}"
        )

    if len(content) > MAX_ATTACHMENT_SIZE:
        raise ValueError(
            f"Attachment exceeds maximum allowed size"
            f"of {MAX_ATTACHMENT_SIZE // (1024 * 1024)} MB."
        )

    if extension == ".txt":
        extracted_text = extract_txt(content)
    elif extension == ".json":
        extracted_text = extract_json(content)
    elif extension == ".csv":
        extracted_text = extract_csv(content)
    elif extension == ".pdf":
        extracted_text = extract_pdf(content)
    else:
        raise ValueError(
            f"Unsupported attachment type: {extension}"
        )

    print("=================================")
    print(f"Attachment: {filename}")
    print("EXTRACTED CONTENT")
    print(extracted_text)
    print("=================================")

    return extracted_text