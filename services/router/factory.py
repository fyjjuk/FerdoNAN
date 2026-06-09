from typing import Dict, Any
from .base import BaseRouter
from .keyword import KeywordRouter
from .ollama import OllamaRouter
from .embedding import EmbeddingRouter
from .hybrid import HybridRouter

def create_router(config: Dict[str, Any]) -> BaseRouter:
    mode = config.get("mode", "keyword")
    threshold = config.get("threshold", 0.3)
    model = config.get("model")
    if mode == "keyword":
        return KeywordRouter(threshold=threshold)
    elif mode == "ollama":
        if not model:
            raise ValueError("Ollama router requiere 'model' en configuración")
        return OllamaRouter(model=model, threshold=threshold)
    elif mode == "embedding":
        return EmbeddingRouter(threshold=threshold)
    elif mode == "hybrid":
        return HybridRouter(
            embedding_threshold=0.7,
            ollama_model=model or "phi3:mini",
            fallback_threshold=threshold
        )
    else:
        raise ValueError(f"Modo de router desconocido: {mode}")
