"""
Tests unitarios para servicios RAG modulares.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock


class TestCollectionManager:
    """Pruebas para CollectionManager."""
    
    def test_init(self):
        from services.rag.collection import CollectionManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CollectionManager(storage_path=tmpdir)
            assert manager.storage_path == tmpdir
            assert manager.client is not None
    
    def test_get_collection_valid_agent(self):
        from services.rag.collection import CollectionManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CollectionManager(storage_path=tmpdir)
            collection = manager.get_collection("test_agent_123")
            assert collection is not None
            assert "test_agent_123" in manager.collection_cache
    
    def test_get_collection_invalid_agent(self):
        from services.rag.collection import CollectionManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CollectionManager(storage_path=tmpdir)
            # Agente con caracteres inválidos
            collection = manager.get_collection("test/agent")
            assert collection is None
    
    def test_delete_collection(self):
        from services.rag.collection import CollectionManager
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = CollectionManager(storage_path=tmpdir)
            # Crear colección primero
            manager.get_collection("test_agent")
            assert "test_agent" in manager.collection_cache
            
            # Eliminar
            manager.delete_collection("test_agent")
            assert "test_agent" not in manager.collection_cache


class TestQueryService:
    """Pruebas para QueryService."""
    
    def test_init(self):
        from services.rag.query import QueryService
        from services.rag.collection import CollectionManager
        
        mock_manager = Mock()
        mock_model = Mock()
        service = QueryService(mock_manager, mock_model)
        assert service.collection_manager == mock_manager
        assert service.model == mock_model
    
    def test_rag_query_empty_query(self):
        from services.rag.query import QueryService
        from services.rag.collection import CollectionManager
        
        mock_manager = Mock()
        mock_model = Mock()
        service = QueryService(mock_manager, mock_model)
        
        result = service.rag_query("test_agent", "", top_k=5)
        
        assert result["documents"] == [[]]
        assert result["distances"] == [[]]
    
    def test_rag_query_invalid_agent(self):
        from services.rag.query import QueryService
        from services.rag.collection import CollectionManager
        
        mock_manager = Mock()
        mock_model = Mock()
        service = QueryService(mock_manager, mock_model)
        
        result = service.rag_query("invalid/agent", "test query", top_k=5)
        
        assert result["documents"] == [[]]


class TestIndexingService:
    """Pruebas para IndexingService."""
    
    def test_init(self):
        from services.rag.indexing import IndexingService
        from services.rag.collection import CollectionManager
        
        mock_manager = Mock()
        mock_model = Mock()
        service = IndexingService(mock_manager, mock_model)
        assert service.collection_manager == mock_manager
        assert service.model == mock_model
    
    def test_index_document_invalid_agent(self):
        from services.rag.indexing import IndexingService
        from services.rag.collection import CollectionManager
        
        mock_manager = Mock()
        mock_model = Mock()
        service = IndexingService(mock_manager, mock_model)
        
        result = service.index_document("invalid/agent", "content", {})
        
        assert result is None
    
    def test_index_conversation_turn(self):
        from services.rag.indexing import IndexingService
        from services.rag.collection import CollectionManager
        
        mock_manager = Mock()
        mock_collection = Mock()
        mock_manager.get_collection.return_value = mock_collection
        mock_model = Mock()
        mock_model.encode.return_value = Mock()
        mock_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
        
        service = IndexingService(mock_manager, mock_model)
        
        # Mockear generate_document_id
        with patch('services.rag.indexing.generate_document_id', return_value="test_id_123"):
            result = service.index_conversation_turn(
                "test_agent", "Hello", "Hi there"
            )
            
            assert result is not None
            mock_collection.add.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
