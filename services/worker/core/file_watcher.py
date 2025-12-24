from watchdog.events import FileSystemEventHandler

class PDFEventHandler(FileSystemEventHandler):
    """
    Handles file system events for the Inbox folder.
    """
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def on_created(self, event):
        if event.is_directory:
            return
        
        if event.src_path.lower().endswith('.pdf'):
            self.pipeline.on_pdf_created(event.src_path)
