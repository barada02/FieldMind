import os
import sys
from pathlib import Path
from typing import List

# Add project root to sys.path to allow imports from backend
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

from pypdf import PdfReader
from backend.rag.vector_store import get_chroma_manager
from backend.app.config import get_settings

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Simple character-based chunking to split long documents into overlapping segments.
    """
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

def ingest_pdf(pdf_path: str):
    """
    Read a PDF, chunk its text, and store it in ChromaDB.
    """
    print(f"Starting ingestion for: {pdf_path}")

    if not Path(pdf_path).exists():
        print(f"Error: File {pdf_path} not found.")
        return

    try:
        # 1. Extract text from PDF
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        if not full_text.strip():
            print("Error: No text could be extracted from the PDF.")
            return

        print(f"Extracted {len(full_text)} characters. Chunking...")

        # 2. Chunk the text
        chunks = chunk_text(full_text)
        print(f"Created {len(chunks)} chunks.")

        # 3. Store in ChromaDB
        manager = get_chroma_manager()

        # Create metadata for each chunk
        metadatas = [{"source": Path(pdf_path).name, "page": "all"} for _ in range(len(chunks))]

        manager.add_documents(
            documents=chunks,
            metadatas=metadatas
        )

        print(f"Successfully ingested {pdf_path} into the vector store.")
        print(f"Total documents in collection: {manager.count_documents()}")

    except Exception as e:
        print(f"An error occurred during ingestion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest a PDF into Field Mind RAG store")
    parser.add_argument("pdf_path", nargs="?", default=r"data\sops\CleaningSOP.pdf", help="Path to the PDF file to ingest (defaults to data\\sops\\CleaningSOP.pdf)")

    args = parser.parse_args()
    ingest_pdf(args.pdf_path)
