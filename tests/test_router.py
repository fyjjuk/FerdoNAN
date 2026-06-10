import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.router.intent_router import Router

def test_router_loading():
    """Router debe cargar correctamente con diferentes modos"""
    # Modo keyword (no requiere modelo)
    r1 = Router(mode="keyword")
    assert r1._config["mode"] == "keyword"
    
    # Modo ollama requiere modelo
    r2 = Router(mode="ollama", model="phi3:mini")
    assert r2._config["mode"] == "ollama"
    assert r2._config["model"] == "phi3:mini"
    
    # Modo embedding (no requiere modelo)
    r3 = Router(mode="embedding")
    assert r3._config["mode"] == "embedding"
    
    # Modo hybrid requiere modelo
    r4 = Router(mode="hybrid", model="phi3:mini")
    assert r4._config["mode"] == "hybrid"
    assert r4._config["model"] == "phi3:mini"
    
    print("✅ Todos los modos de router se instancian correctamente")
