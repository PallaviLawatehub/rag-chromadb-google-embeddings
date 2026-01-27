from pypdf import PdfReader
from docx import Document
import io

def extract_text_from_files(uploaded_files):
    """
    Extract text content from uploaded PDF, TXT, and DOCX files.

    Args:
        uploaded_files (list): List of Streamlit UploadedFile objects.

    Returns:
        str: Combined text content from all files.
    """
    combined_text = ""

    for uploaded_file in uploaded_files:
        file_type = uploaded_file.name.split('.')[-1].lower()

        if file_type == 'pdf':
            # Read PDF
            pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
            for page in pdf_reader.pages:
                combined_text += page.extract_text() + "\n"

        elif file_type == 'txt':
            # Read TXT
            combined_text += uploaded_file.read().decode('utf-8') + "\n"

        elif file_type == 'docx':
            # Read DOCX
            doc = Document(io.BytesIO(uploaded_file.read()))
            for para in doc.paragraphs:
                combined_text += para.text + "\n"

        else:
            # Skip unsupported files
            continue

    return combined_text.strip()

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into chunks of specified size with overlap.

    Args:
        text (str): The text to chunk.
        chunk_size (int): Size of each chunk in characters. Default 500.
        overlap (int): Number of overlapping characters between chunks. Default 50.

    Returns:
        list: List of text chunks.
    """
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
        if start >= len(text):
            break

    return chunks