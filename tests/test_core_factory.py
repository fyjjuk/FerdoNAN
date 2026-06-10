"""
Tests para core/factory.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from core.factory import create_router, create_sanitizer


class TestCoreFactory:
    """Pruebas para las factorías de core"""
    
    def test_create_router_with_keyword_mode(self):
        """Verificar creación de router en modo keyword"""
        mock_manifest = Mock()
        mock_manifest.router_config.mode = "keyword"
        mock_manifest.router_config.model = None
        mock_manifest.router_config.threshold = 0.3
        
        with patch('core.factory.Router') as mock_router:
            mock_router.return_value = MagicMock()
            router = create_router(mock_manifest)
            
            mock_router.assert_called_once_with(mode="keyword", model=None, threshold=0.3)
            assert router is not None
    
    def test_create_router_with_embedding_mode(self):
        """Verificar creación de router en modo embedding"""
        mock_manifest = Mock()
        mock_manifest.router_config.mode = "embedding"
        mock_manifest.router_config.model = "all-MiniLM-L6-v2"
        mock_manifest.router_config.threshold = 0.5
        
        with patch('core.factory.Router') as mock_router:
            mock_router.return_value = MagicMock()
            router = create_router(mock_manifest)
            
            mock_router.assert_called_once_with(mode="embedding", model="all-MiniLM-L6-v2", threshold=0.5)
            assert router is not None
    
    def test_create_sanitizer_enabled(self):
        """Verificar creación de sanitizador habilitado"""
        mock_manifest = Mock()
        mock_manifest.sanitizer_config.enabled = True
        mock_manifest.sanitizer_config.model = "phi3:mini"
        
        with patch('core.factory.Sanitizer') as mock_sanitizer:
            mock_sanitizer.return_value = MagicMock()
            sanitizer = create_sanitizer(mock_manifest)
            
            mock_sanitizer.assert_called_once_with(enabled=True, model="phi3:mini")
            assert sanitizer is not None
    
    def test_create_sanitizer_disabled(self):
        """Verificar creación de sanitizador deshabilitado"""
        mock_manifest = Mock()
        mock_manifest.sanitizer_config.enabled = False
        mock_manifest.sanitizer_config.model = None
        
        with patch('core.factory.Sanitizer') as mock_sanitizer:
            mock_sanitizer.return_value = MagicMock()
            sanitizer = create_sanitizer(mock_manifest)
            
            mock_sanitizer.assert_called_once_with(enabled=False, model=None)
            assert sanitizer is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
