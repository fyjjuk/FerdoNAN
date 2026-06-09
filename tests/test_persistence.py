"""Tests para persistencia: memoria a corto y largo plazo."""
import sys
import os
import tempfile
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from persistence.memory_store import ShortTermMemory
from persistence.long_term_memory import LongTermMemory
from persistence.cache import ResponseCache
from persistence.backup import BackupManager


class TestShortTermMemory:
    """Tests para memoria a corto plazo."""

    def test_memory_add_and_get_context(self, tmp_path):
        """ShortTermMemory debe almacenar y recuperar mensajes."""
        # Usar directorio temporal para pruebas
        with patch('persistence.memory_store.os.path.exists', return_value=False):
            memory = ShortTermMemory(window_size=3, agent_id="test_agent")
            memory._get_memory_file = lambda: str(tmp_path / "memory.json")
            
            memory.add("Mensaje 1")
            memory.add("Mensaje 2")
            memory.add("Mensaje 3")
            
            context = memory.get_context()
            assert len(context) == 3
            assert "Mensaje 1" in context

    def test_memory_evicts_oldest(self, tmp_path):
        """ShortTermMemory debe eliminar el mensaje más antiguo cuando excede window_size."""
        with patch('persistence.memory_store.os.path.exists', return_value=False):
            memory = ShortTermMemory(window_size=2, agent_id="test_agent")
            memory._get_memory_file = lambda: str(tmp_path / "memory.json")
            
            memory.add("Primero")
            memory.add("Segundo")
            memory.add("Tercero")
            
            context = memory.get_context()
            assert len(context) == 2
            assert "Primero" not in context
            assert "Segundo" in context
            assert "Tercero" in context

    def test_memory_clear(self, tmp_path):
        """ShortTermMemory debe limpiar todos los mensajes."""
        with patch('persistence.memory_store.os.path.exists', return_value=False):
            memory = ShortTermMemory(window_size=5, agent_id="test_agent")
            memory._get_memory_file = lambda: str(tmp_path / "memory.json")
            
            memory.add("Mensaje 1")
            memory.add("Mensaje 2")
            memory.clear()
            
            assert len(memory.get_context()) == 0


class TestResponseCache:
    """Tests para caché de respuestas."""

    def test_cache_hit_and_miss(self, tmp_path):
        """ResponseCache debe acertar en caché cuando está presente."""
        cache = ResponseCache(cache_dir=str(tmp_path), ttl_seconds=3600)
        
        # Inicialmente no debería estar en caché
        assert cache.get("agent1", "route1", "prompt") is None
        
        # Almacenar
        cache.set("agent1", "route1", "prompt", "respuesta cacheada")
        
        # Debería encontrar
        result = cache.get("agent1", "route1", "prompt")
        assert result == "respuesta cacheada"

    def test_cache_expires(self, tmp_path):
        """ResponseCache debe expirar entradas antiguas."""
        cache = ResponseCache(cache_dir=str(tmp_path), ttl_seconds=0.1)
        
        cache.set("agent1", "route1", "prompt", "respuesta")
        assert cache.get("agent1", "route1", "prompt") == "respuesta"
        
        # Esperar a que expire
        import time
        time.sleep(0.2)
        
        assert cache.get("agent1", "route1", "prompt") is None

    def test_cache_different_agents_isolated(self, tmp_path):
        """ResponseCache debe aislar cachés por agente."""
        cache = ResponseCache(cache_dir=str(tmp_path))
        
        cache.set("agent1", "route1", "prompt", "respuesta_agent1")
        cache.set("agent2", "route1", "prompt", "respuesta_agent2")
        
        assert cache.get("agent1", "route1", "prompt") == "respuesta_agent1"
        assert cache.get("agent2", "route1", "prompt") == "respuesta_agent2"


class TestBackupManager:
    """Tests para BackupManager."""

    def test_create_backup(self, tmp_path):
        """BackupManager debe crear archivo de backup."""
        with patch('persistence.backup.Path', return_value=tmp_path):
            backup_mgr = BackupManager(backup_dir=str(tmp_path))
            
            # Crear archivo temporal para backup
            test_file = tmp_path / "test.txt"
            test_file.write_text("contenido de prueba")
            
            backup_path = backup_mgr.create_backup(name="test_backup")
            assert backup_path.exists()
            assert backup_path.suffix == ".gz"

    def test_list_backups(self, tmp_path):
        """BackupManager debe listar backups existentes."""
        backup_mgr = BackupManager(backup_dir=str(tmp_path))
        
        # Crear backups simulados
        (tmp_path / "backup1.tar.gz").touch()
        (tmp_path / "backup2.tar.gz").touch()
        
        backups = backup_mgr.list_backups()
        assert len(backups) == 2
        assert any("backup1" in b["name"] for b in backups)


# Necesario para parchear en tests
from unittest.mock import patch


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
