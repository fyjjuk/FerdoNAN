"""
Tests para servicios RAG
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestRAGUtils:
    """Pruebas para utilidades RAG"""
    
    def test_validate_agent_id_valid(self):
        from services.rag.utils import validate_agent_id
        assert validate_agent_id("test_agent-123") is True
        assert validate_agent_id("valid_agent") is True
        assert validate_agent_id("agent-v2.0") is False  # punto no permitido
        assert validate_agent_id("") is False
        assert validate_agent_id(None) is False
    
    def test_sanitize_query(self):
        from services.rag.utils import sanitize_query
        query = "  test query  "
        result = sanitize_query(query)
        assert result == "test query"
        
        # Query muy largo
        long_query = "x" * 2000
        result = sanitize_query(long_query, max_length=1000)
        assert len(result) == 1000
        
        # Input inválido
        assert sanitize_query(None) == ""
        assert sanitize_query(123) == ""
    
    def test_generate_document_id(self):
        from services.rag.utils import generate_document_id
        doc_id = generate_document_id("agent1", "content", "timestamp")
        assert isinstance(doc_id, str)
        assert len(doc_id) == 32  # MD5 hex length


class TestCollectionManager:
    """Pruebas para CollectionManager"""
    
    def test_init(self):
        from services.rag.collection import CollectionManager
        with patch('chromadb.PersistentClient') as mock_client:
            manager = CollectionManager("/tmp/test")
            assert manager.storage_path == "/tmp/test"
    
    def test_get_collection_invalid_agent(self):
        from services.rag.collection import CollectionManager
        with patch('chromadb.PersistentClient'):
            manager = CollectionManager("/tmp/test")
            result = manager.get_collection("")
            assert result is None


class TestRAGEngine:
    """Pruebas para RAGEngine (API de compatibilidad)"""
    
    def test_rag_engine_import(self):
        from services.rag import RAGEngine
        with patch('sentence_transformers.SentenceTransformer'):
            with patch('services.rag.collection.CollectionManager'):
                engine = RAGEngine("/tmp/test")
                assert engine is not None
                assert hasattr(engine, 'index_document')
                assert hasattr(engine, 'rag_query')
                assert hasattr(engine, 'delete_namespace')
    
    def test_legacy_vector_store_import(self):
        from services.vector_store import RAGEngine
        assert RAGEngine is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
