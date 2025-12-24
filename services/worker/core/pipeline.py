import logging
import asyncio
import shutil
import os
from core.interfaces import ParserProto, EmbedderProto, DataStoreProto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkerPipeline:
    def __init__(self, parser: ParserProto, embedder: EmbedderProto, store: DataStoreProto, processed_dir: str = None):
        self.parser = parser
        self.embedder = embedder
        self.store = store
        self.processed_dir = processed_dir

    def on_pdf_created(self, file_path: str):
        """
        Entry point for the watcher.
        Since the watcher is synchronous, we create a task.
        """
        logger.info(f"Detected new PDF: {file_path}")
        asyncio.run(self.process_file(file_path))

    async def process_file(self, file_path: str):
        try:
            # 1. Parse
            logger.info(f"Parsing {file_path}...")
            parsed_data = self.parser.parse(file_path)
            
            # 2. Embed
            text = parsed_data.get("text", "")
            if not text:
                logger.warning(f"No text extracted from {file_path}")
                return

            logger.info(f"Embedding content from {file_path}...")
            vector = await self.embedder.get_embedding(text)
            
            # 3. Save
            document = parsed_data.copy()
            document["vector"] = vector
            
            logger.info(f"Saving document {file_path}...")
            await self.store.save_document(document)
            
            logger.info(f"Successfully processed {file_path}")

            # 4. Move to processed
            if self.processed_dir:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(self.processed_dir, filename)
                logger.info(f"Moving {file_path} to {dest_path}")
                shutil.move(file_path, dest_path)
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

