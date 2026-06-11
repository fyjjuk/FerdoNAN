"""Tests para el nuevo sistema de caché por agente."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from persistence.cache.file_cache import FileCache
from persistence.cache.strategy import should_cache
from persistence.cache.interface import CacheInterface


class TestFileCache:
    """Pruebas para FileCache."""
    
    def test_init_creates_directory(self):
        """Verificar que el directorio de caché se crea."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache("test_agent", enabled=True, ttl=3600)
            # Sobrescribir cache_dir para usar tmpdir
            cache.cache_dir = tmpdir
            assert os.path.exists(tmpdir)
    
    def test_set_and_get(self):
        """Verificar almacenamiento y recuperación."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache("test_agent", enabled=True, ttl=3600)
            cache.cache_dir = tmpdir
            cache.set("test_route", "test query", "test response")
            result = cache.get("test_route", "test query")
            assert result == "test response"
    
    def test_get_expired(self):
        """Verificar que las entradas expiradas no se devuelven."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache("test_agent", enabled=True, ttl=-1)  # Expirado inmediatamente
            cache.cache_dir = tmpdir
            cache.set("test_route", "test query", "test response")
            result = cache.get("test_route", "test query")
            assert result is None
    
    def test_disabled_cache(self):
        """Verificar que cuando está deshabilitado, no almacena ni recupera."""
        cache = FileCache("test_agent", enabled=False, ttl=3600)
        cache.set("test_route", "test query", "test response")
        result = cache.get("test_route", "test query")
        assert result is None
    
    def test_invalidate_route(self):
        """Verificar invalidación por ruta."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache("test_agent", enabled=True, ttl=3600)
            cache.cache_dir = tmpdir
            cache.set("route1", "query1", "response1")
            cache.set("route2", "query2", "response2")
            cache.invalidate(route_id="route1")
            assert cache.get("route1", "query1") is None
            assert cache.get("route2", "query2") == "response2"
    
    def test_clear_agent_cache(self):
        """Verificar limpieza completa del caché del agente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache("test_agent", enabled=True, ttl=3600)
            cache.cache_dir = tmpdir
            cache.set("route1", "query1", "response1")
            cache.set("route2", "query2", "response2")
            cache.clear_agent_cache()
            assert cache.get("route1", "query1") is None
            assert cache.get("route2", "query2") is None


class TestStrategy:
    """Pruebas para la estrategia de caché."""
    
    def test_should_cache_cognitive_route(self):
        """Las rutas cognitivas deben cachearse."""
        intent = {"type": "cognitive"}
        assert should_cache(intent, True) is True
    
    def test_should_not_cache_script_route(self):
        """Las rutas script NO deben cachearse."""
        intent = {"type": "script"}
        assert should_cache(intent, True) is False
    
    def test_should_not_cache_when_disabled(self):
        """Cuando el agente tiene caché deshabilitado, no debe cachear."""
        intent = {"type": "cognitive"}
        assert should_cache(intent, False) is False
    
    def test_should_cache_stages_route(self):
        """Rutas con stages deben cachearse."""
        intent = {"type": "cognitive", "stages": [{"name": "stage1"}]}
        assert should_cache(intent, True) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
