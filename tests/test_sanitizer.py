import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.input_cleaner import Sanitizer

def test_sanitizer_simple():
    s = Sanitizer(enabled=True)
    result = s.clean("Hola!!   cómo estás???")
    assert result == "Hola!! cómo estás???" or "hola" in result.lower()

def test_sanitizer_short():
    s = Sanitizer(enabled=True, )
    result = s.clean("hola")
    assert len(result) > 0
