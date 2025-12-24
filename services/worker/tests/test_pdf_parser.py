import os
import pytest
from core.pdf_parser import PDFParser
from pypdf import PdfWriter

@pytest.fixture
def sample_pdf(tmp_path):
    """Creates a simple PDF file for testing."""
    pdf_path = tmp_path / "test.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    
    # We can't easily add text without reportlab or similar, 
    # so for now we might test metadata or just basic valid file check.
    # Or we can modify this to use a library if we really need text extraction test.
    # For now, let's just create a valid PDF structure.
    
    with open(pdf_path, "wb") as f:
        writer.write(f)
        
    return str(pdf_path)

def test_parse_exists(sample_pdf):
    parser = PDFParser()
    result = parser.parse(sample_pdf)
    assert result is not None
    assert "metadata" in result
    assert "text" in result

def test_parse_metadata(sample_pdf):
    # This test is limited because pypdf blank page doesn't have much metadata
    # But we check the structure
    parser = PDFParser()
    result = parser.parse(sample_pdf)
    assert isinstance(result['metadata'], dict)
