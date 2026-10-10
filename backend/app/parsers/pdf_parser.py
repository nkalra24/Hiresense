from pathlib import Path
import pymupdf as fitz  # PyMuPDF (modern import)

def extract_text_from_pdf(file_path: Path | str) -> str:
    """
    Extracts text cleanly from a PDF document using PyMuPDF.
    Handles encryption, corruption, and empty documents with explicit error messages.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    try:
        doc = fitz.open(str(path))
    except Exception as e:
        raise ValueError(f"Corrupted or invalid PDF file: {str(e)}")

    try:
        if doc.is_encrypted:
            # Try authenticating with empty password if just marked encrypted
            if not doc.authenticate(""):
                raise ValueError("PDF is encrypted and password-protected")

        extracted_pages = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")
            if page_text:
                extracted_pages.append(page_text.strip())

        full_text = "\n\n".join(extracted_pages).strip()

        if not full_text:
            raise ValueError("PDF contains no extractable text (document may be a scanned image or empty)")

        return full_text
    finally:
        doc.close()
