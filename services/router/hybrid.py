from typing import List, Dict, Any, Tuple, Optional
from core.logger import logger
from .base import BaseRouter
from .embedding import EmbeddingRouter
from .ollama import OllamaRouter

class HybridRouter(BaseRouter):
    def __init__(self, embedding_threshold: float = 0.7, ollama_model: str = "phi3:mini", fallback_threshold: float = 0.3):
        self.embedding = EmbeddingRouter(threshold=embedding_threshold)
        self.ollama = OllamaRouter(model=ollama_model)
        self.fallback_threshold = fallback_threshold

    def route(self, routes: List[Dict[str, Any]], user_input: str, threshold: Optional[float] = None) -> Tuple[str, float, Dict]:
        # 1. Embedding
        route_id, score, route = self.embedding.route(routes, user_input)
        if route_id:
            logger.info(f"HybridRouter: embedding alta confianza: {route_id} (score={score:.2f})")
            return route_id, score, route
        # 2. Si score es bajo pero no nulo, usar LLM
        if score >= self.fallback_threshold:
            logger.info(f"HybridRouter: embedding score medio ({score:.2f}), usando Ollama")
            ollama_id, _, ollama_route = self.ollama.route(routes, user_input)
            if ollama_id:
                return ollama_id, 1.0, ollama_route
        # 3. Fallback a embedding bajo (o primera ruta)
        if route:
            return route_id, score, route
        return None, 0.0, None
