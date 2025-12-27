import pytest
from core.chunker import RecursiveCharacterTextSplitter

def test_simple_split():
    text = "Hello world. This is a test."
    splitter = RecursiveCharacterTextSplitter(chunk_size=10, chunk_overlap=0, separators=[" "])
    chunks = splitter.split_text(text)
    # "Hello" is 5. "world." is 6. "Hello world." is 12 > 10.
    # So it should be ["Hello", "world.", "This is", "a test."] or similar logic.
    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk) <= 10 or len(chunk.split(" ")[0]) > 10 # Handling single long words

def test_long_text_split():
    text = "a" * 100 + " " + "b" * 100
    splitter = RecursiveCharacterTextSplitter(chunk_size=110, chunk_overlap=0)
    chunks = splitter.split_text(text)
    assert len(chunks) == 2
    assert chunks[0] == "a" * 100
    assert chunks[1] == "b" * 100

def test_overlap():
    text = "1234567890"
    splitter = RecursiveCharacterTextSplitter(chunk_size=5, chunk_overlap=2, separators=[""])
    chunks = splitter.split_text(text)
    # Expected: 
    # "12345"
    # Overlap 2 -> start next from "45..." -> "45678"
    # Overlap 2 -> start next from "78..." -> "7890"
    
    assert "12345" in chunks
    assert "45678" in chunks
    
def test_hierarchy_separators():
    # Should split by \n\n first, then \n, then space
    text = "Paragraph 1.\n\nParagraph 2 is very long... " + ("word " * 50)
    splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
    chunks = splitter.split_text(text)
    
    assert len(chunks) > 1
    # Check that it didn't split "Paragraph 1." if it fits
    assert "Paragraph 1." in chunks[0] or chunks[0].startswith("Paragraph 1")
