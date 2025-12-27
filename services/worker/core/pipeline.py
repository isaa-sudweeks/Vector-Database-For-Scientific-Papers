import logging
import asyncio
import shutil
import os
from core.interfaces import ParserProto, EmbedderProto, DataStoreProto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkerPipeline:
    def __init__(self, parser: ParserProto, embedder: EmbedderProto, store: DataStoreProto, chunker, processed_dir: str = None):
        self.parser = parser
        self.embedder = embedder
        self.store = store
        self.chunker = chunker
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
            
            # 2. Chunk and Embed
            original_text = parsed_data.get("text", "")
            if not original_text:
                logger.warning(f"No text extracted from {file_path}")
                return

            chunks = self.chunker.split_text(original_text)
            logger.info(f"Split {file_path} into {len(chunks)} chunks.")

            for i, chunk_text in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)} for {file_path}...")
                
                # Embed
                vector = await self.embedder.get_embedding(chunk_text)
                
                # 3. Save
                document = parsed_data.copy()
                document["text"] = chunk_text # Store only the chunk text
                document["vector"] = vector
                document["chunk_index"] = i
                document["total_chunks"] = len(chunks)
                # Ideally generate a parent_id, but filename acts as one for now
                
                await self.store.save_document(document)
            
            logger.info(f"Successfully processed {file_path} ({len(chunks)} chunks)")

            # 4. Move to processed
            if self.processed_dir:
                filename = os.path.basename(file_path)
                dest_path = os.path.join(self.processed_dir, filename)
                logger.info(f"Moving {file_path} to {dest_path}")
                shutil.move(file_path, dest_path)
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

