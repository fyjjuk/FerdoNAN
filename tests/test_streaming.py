"""
Tests para services/executor/streaming.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from services.executor.streaming import StreamHandler


class TestStreaming:
    """Pruebas para StreamHandler"""
    
    def test_stream_with_yield_native_support(self):
        """Verificar streaming con LLM que soporta stream_response"""
        mock_llm = Mock()
        # Simular un iterador
        mock_llm.stream_response.return_value = iter(["Hello", " ", "World"])
        
        tokens = list(StreamHandler.stream_with_yield(mock_llm, "prompt", "system", {}))
        
        assert tokens == ["Hello", " ", "World"]
        mock_llm.stream_response.assert_called_once()
    
    def test_stream_with_yield_fallback(self):
        """Verificar fallback cuando LLM no soporta streaming"""
        mock_llm = Mock()
        mock_llm.generate_response.return_value = "Complete response"
        # Eliminar el atributo stream_response para simular que no existe
        if hasattr(mock_llm, 'stream_response'):
            del mock_llm.stream_response
        
        tokens = list(StreamHandler.stream_with_yield(mock_llm, "prompt", "system", {}))
        
        assert tokens == ["Complete response"]
        mock_llm.generate_response.assert_called_once()
    
    def test_stream_response_legacy(self):
        """Verificar método legacy de compatibilidad"""
        mock_llm = Mock()
        mock_llm.stream_response.return_value = iter(["Token1", "Token2", "Token3"])
        
        result = StreamHandler.stream_response_legacy(mock_llm, "prompt", "system", {})
        
        assert result == "Token1Token2Token3"
    
    def test_stream_with_yield_empty_tokens(self):
        """Verificar streaming con tokens vacíos"""
        mock_llm = Mock()
        mock_llm.stream_response.return_value = iter([])
        
        tokens = list(StreamHandler.stream_with_yield(mock_llm, "prompt", "system", {}))
        
        assert tokens == []
    
    def test_stream_with_yield_single_token(self):
        """Verificar streaming con un solo token"""
        mock_llm = Mock()
        mock_llm.stream_response.return_value = iter(["SingleToken"])
        
        tokens = list(StreamHandler.stream_with_yield(mock_llm, "prompt", "system", {}))
        
        assert tokens == ["SingleToken"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
