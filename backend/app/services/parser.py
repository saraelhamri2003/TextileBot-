import os
from pypdf import PdfReader
import docx
from typing import List

class DocumentParser:
    @staticmethod
    def extract_text_from_pdf(filepath: str) -> str:
        try:
            reader = PdfReader(filepath)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    @staticmethod
    def extract_text_from_docx(filepath: str) -> str:
        try:
            doc = docx.Document(filepath)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")

    @staticmethod
    def extract_text_from_txt(filepath: str) -> str:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Failed to parse TXT: {str(e)}")

    @classmethod
    def extract_text(cls, filepath: str, file_type: str) -> str:
        if file_type == "pdf":
            return cls.extract_text_from_pdf(filepath)
        elif file_type == "docx":
            return cls.extract_text_from_docx(filepath)
        elif file_type == "txt":
            return cls.extract_text_from_txt(filepath)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
        chunks = []
        if not text:
            return chunks
        
        words = text.split()
        current_chunk = []
        current_size = 0
        
        # Word-based chunking for cleaner text blocks
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1 # +1 for space
            
            if current_size >= chunk_size:
                chunks.append(" ".join(current_chunk))
                # Retain overlap words
                overlap_words = current_chunk[-max(1, int(overlap / 6)):] # estimate 6 chars per word
                current_chunk = list(overlap_words)
                current_size = sum(len(w) + 1 for w in current_chunk)
                
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return [c for c in chunks if c.strip()]
