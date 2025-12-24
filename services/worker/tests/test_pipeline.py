import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.pipeline import WorkerPipeline
from core.interfaces import ParserProto, EmbedderProto, DataStoreProto

@pytest.mark.asyncio
async def test_pipeline_flow():
    # Mocks
    mock_parser = MagicMock(spec=ParserProto)
    mock_parser.parse.return_value = {
        "text": "test content",
        "metadata": {"title": "Test PDF"},
        "filename": "test.pdf"
    }
    
    mock_embedder = AsyncMock(spec=EmbedderProto)
    mock_embedder.get_embedding.return_value = [0.1, 0.2, 0.3]
    
    mock_store = AsyncMock(spec=DataStoreProto)
    mock_store.save_document.return_value = True
    
    # Patch shutil.move
    with patch('shutil.move') as mock_move:
        # Init Pipeline
        pipeline = WorkerPipeline(
            parser=mock_parser,
            embedder=mock_embedder,
            store=mock_store,
            processed_dir="/app/processed"
        )
        
        # Trigger
        # We need a file path that looks real enough or we just mock os.path.exists if needed by move?
        # shutil.move usually just tries. 
        await pipeline.process_file("/path/to/test.pdf")
        
        # Verify
        mock_parser.parse.assert_called_once_with("/path/to/test.pdf")
        mock_embedder.get_embedding.assert_awaited_once_with("test content")
        
        # Check what was saved
        expected_doc = {
            "text": "test content",
            "metadata": {"title": "Test PDF"},
            "filename": "test.pdf",
            "vector": [0.1, 0.2, 0.3]
        }
        mock_store.save_document.assert_awaited_once_with(expected_doc)
        
        # Verify move
        mock_move.assert_called_once_with("/path/to/test.pdf", "/app/processed/test.pdf")


@pytest.mark.asyncio
async def test_pipeline_handles_errors():
    mock_parser = MagicMock(spec=ParserProto)
    mock_parser.parse.side_effect = Exception("Parse Error")
    
    with patch('shutil.move') as mock_move:
        pipeline = WorkerPipeline(
            parser=mock_parser,
            embedder=AsyncMock(),
            store=AsyncMock(),
            processed_dir="/app/processed"
        )
        
        # Should not raise exception (it should log it)
        await pipeline.process_file("bad.pdf")
        
        # Verify execution stopped
        pipeline.embedder.get_embedding.assert_not_called()
        
        # Verify NO move
        mock_move.assert_not_called()

