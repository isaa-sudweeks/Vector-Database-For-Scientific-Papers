import time
import os
import pytest
from watchdog.observers import Observer
from core.file_watcher import PDFEventHandler

class MockPipeline:
    def __init__(self):
        self.processed_files = []

    def on_pdf_created(self, file_path):
        self.processed_files.append(file_path)

def test_handler_triggers_pipeline(tmp_path):
    # Setup
    mock_pipeline = MockPipeline()
    handler = PDFEventHandler(mock_pipeline)
    
    # Create a dummy event object (mocking watchdog event)
    class MockEvent:
        def __init__(self, src_path):
            self.src_path = src_path
            self.is_directory = False
            
    # Simulate file creation event
    new_file = tmp_path / "test.pdf"
    event = MockEvent(str(new_file))
    
    # Trigger
    handler.on_created(event)
    
    # Assert
    assert str(new_file) in mock_pipeline.processed_files

def test_handler_ignores_non_pdf(tmp_path):
    mock_pipeline = MockPipeline()
    handler = PDFEventHandler(mock_pipeline)
    
    class MockEvent:
        def __init__(self, src_path):
            self.src_path = src_path
            self.is_directory = False
            
    # Simulate text file creation
    new_file = tmp_path / "test.txt"
    event = MockEvent(str(new_file))
    
    handler.on_created(event)
    
    assert str(new_file) not in mock_pipeline.processed_files
