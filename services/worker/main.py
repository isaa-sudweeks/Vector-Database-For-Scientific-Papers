import time
import os
import signal
import sys
from watchdog.observers import Observer
from core.file_watcher import PDFEventHandler
from core.pipeline import WorkerPipeline
from core.pdf_parser import PDFParser
from core.embedder import RemoteEmbedder
from core.store import QdrantStore
from core.chunker import RecursiveCharacterTextSplitter
import yaml

# Config
INBOX_DIR = os.getenv("INBOX_DIR", "/app/inbox")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "/app/processed")
EMBEDDING_SERVICE_URL = os.getenv("EMBEDDING_SERVICE_URL", "http://embeddings:8001")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

def main():
    print("Starting Worker Service...")
    
    # Ensure Inbox and Processed dirs exist
    if not os.path.exists(INBOX_DIR):
        print(f"Creating inbox directory: {INBOX_DIR}")
        os.makedirs(INBOX_DIR, exist_ok=True)

    if not os.path.exists(PROCESSED_DIR):
        print(f"Creating processed directory: {PROCESSED_DIR}")
        os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Load Config
    try:
        with open("/app/config.yaml", "r") as f:
            config = yaml.safe_load(f)
            chunking_config = config.get("chunking", {})
            chunk_size = chunking_config.get("chunk_size", 1000)
            chunk_overlap = chunking_config.get("chunk_overlap", 200)
            print(f"Loaded config: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    except FileNotFoundError:
        print("Config file not found, using defaults.")
        chunk_size = 1000
        chunk_overlap = 200

    # Initialize Components
    parser = PDFParser()
    embedder = RemoteEmbedder(EMBEDDING_SERVICE_URL)
    store = QdrantStore(QDRANT_HOST, QDRANT_PORT)
    chunker = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    pipeline = WorkerPipeline(parser, embedder, store, chunker, processed_dir=PROCESSED_DIR)
    event_handler = PDFEventHandler(pipeline)
    
    observer = Observer()
    observer.schedule(event_handler, INBOX_DIR, recursive=False)
    observer.start()
    print(f"Watching for PDFs in {INBOX_DIR}...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    main()
