import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.intent_router import Router

def test_router_loading():
    r = Router(mode="ollama")  # No se ejecuta realmente, solo instancia
    assert r.mode == "ollama"
