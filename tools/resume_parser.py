"""Resume parser for PDF and text files."""

import io
from pathlib import Path
from typing import Optional


def parse_resume_pdf(file_bytes: bytes) -> str:
    """Parse a PDF resume into text.
    
    Args:
        file_bytes: Raw bytes of the PDF file
        
    Returns:
        Extracted text from the PDF
    """
    try:
        from PyPDF2 import PdfReader
        
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n".join(text_parts)
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"


def parse_resume_docx(file_bytes: bytes) -> str:
    """Parse a DOCX resume into text.
    
    Args:
        file_bytes: Raw bytes of the DOCX file
        
    Returns:
        Extracted text from the document
    """
    try:
        from docx import Document
        
        docx_file = io.BytesIO(file_bytes)
        doc = Document(docx_file)
        
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        return "\n".join(text_parts)
    except Exception as e:
        return f"Error parsing DOCX: {str(e)}"


def parse_resume(file_bytes: bytes, filename: str) -> str:
    """Parse a resume file based on its extension.
    
    Args:
        file_bytes: Raw bytes of the file
        filename: Original filename to determine type
        
    Returns:
        Extracted text from the resume
    """
    ext = Path(filename).suffix.lower()
    
    if ext == ".pdf":
        return parse_resume_pdf(file_bytes)
    elif ext in [".docx", ".doc"]:
        return parse_resume_docx(file_bytes)
    elif ext == ".txt":
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        return f"Unsupported file format: {ext}. Please upload PDF, DOCX, or TXT."


def save_resume_text(text: str, user_id: str, data_dir: Path) -> Path:
    """Save parsed resume text to file.
    
    Args:
        text: Resume text content
        user_id: Telegram user ID
        data_dir: Directory to save files
        
    Returns:
        Path to saved file
    """
    filepath = data_dir / f"resume_{user_id}.txt"
    filepath.write_text(text, encoding="utf-8")
    return filepath


def load_resume_text(user_id: str, data_dir: Path) -> Optional[str]:
    """Load saved resume text for a user.
    
    Args:
        user_id: Telegram user ID
        data_dir: Directory where files are saved
        
    Returns:
        Resume text or None if not found
    """
    filepath = data_dir / f"resume_{user_id}.txt"
    if filepath.exists():
        return filepath.read_text(encoding="utf-8")
    return None
