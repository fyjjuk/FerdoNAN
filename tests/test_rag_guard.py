import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.intent_router import RAGGuard

def test_rag_guard_initialization():
    guard = RAGGuard(domains=["test"], threshold=0.5)
    assert guard.threshold == 0.5
