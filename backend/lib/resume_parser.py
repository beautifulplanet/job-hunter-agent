import pdfplumber
import docx
import os
import re


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber for much cleaner output."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    raw = "\n".join(text_parts)
    # Post-process: collapse excessive whitespace while keeping paragraph breaks
    raw = re.sub(r'[ \t]+', ' ', raw)         # collapse horizontal whitespace
    raw = re.sub(r'\n{3,}', '\n\n', raw)      # max 2 newlines (paragraph break)
    raw = re.sub(r' *\n *', '\n', raw)        # trim spaces around newlines
    return raw.strip()


def extract_text_from_docx(docx_path: str) -> str:
    doc = docx.Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def extract_text(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext.lower() == '.docx':
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
