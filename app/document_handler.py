import pdfplumber
from docx import Document
from fastapi import UploadFile
from typing import List

def extract_text(file: UploadFile):
    """
    Extract text from supported uploads (.pdf, .docx, .txt).
    Works with UploadFile-like objects that have .file (a file-like object) and .filename.
    Returns full text (string).
    """
    name = getattr(file, "filename", "")
    # Normalize lower
    if name.lower().endswith(".pdf"):
        with pdfplumber.open(file.file) as pdf:
            texts = []
            for page in pdf.pages:
                texts.append(page.extract_text() or "")
            return "\n".join(texts)
    elif name.lower().endswith(".docx"):
        doc = Document(file.file)
        return "\n".join(p.text for p in doc.paragraphs)
    elif name.lower().endswith(".txt"):
        return file.file.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file type: " + name)

def split_text(text: str, max_tokens=500) -> List[str]:
    words = text.split()
    return [" ".join(words[i:i+max_tokens]) for i in range(0, len(words), max_tokens)]
