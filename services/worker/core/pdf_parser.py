from pypdf import PdfReader
import os

class PDFParser:
    def parse(self, file_path: str) -> dict:
        """
        Parses a PDF file and extracts text and metadata.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        reader = PdfReader(file_path)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            
        metadata = reader.metadata or {}
        
        # Convert PdfDict to regular dict and clean keys
        clean_metadata = {}
        if metadata:
            for key, value in metadata.items():
                if isinstance(key, str):
                    # Remove the '/' prefix often found in PDF metadata keys
                    clean_key = key.lstrip('/')
                    clean_metadata[clean_key] = str(value)

        return {
            "text": text,
            "metadata": clean_metadata,
            "filename": os.path.basename(file_path)
        }
