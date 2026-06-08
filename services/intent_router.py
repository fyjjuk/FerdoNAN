import os
import yaml
import re
import requests
from typing import List, Dict, Any, Tuple
from core.logger import logger
from sentence_transformers import SentenceTransformer, util

class RouteNotFoundError(Exception):
    def __init__(self, message: str, available_routes: List[Dict[str, Any]]):
        super().__init__(message)
        self.available_routes = available_routes

class RAGGuard:
    def __init__(self, domains: List[str], threshold: float = 0.4):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.domains_emb = self.model.encode(domains, convert_to_tensor=True)
        self.threshold = threshold
        logger.info(f"RAGGuard inicializado con {len(domains)} dominios, umbral={threshold}")

    def needs_rag(self, query: str) -> Tuple[bool, float]:
        query_emb = self.model.encode(query, convert_to_tensor=True)
        scores = util.cos_sim(query_emb, self.domains_emb)[0]
        max_sim = float(scores.max())
        needed = max_sim > self.threshold
        logger.debug(f"RAGGuard: query='{query[:50]}...', max_sim={max_sim:.3f}, needed={needed}")
        return needed, max_sim

class Router:
    def __init__(self, mode: str = "ollama", model: str = "llama3.2:3b", rag_domains: List[str] = None):
        self.mode = mode
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.rag_guard = RAGGuard(domains=rag_domains or ["técnico", "documentación", "manual", "reglas", "bestiario", "hechizos"])

    def _load_agent_routes(self, agent_id: str) -> List[Dict[str, Any]]:
        routes_dir = os.path.join("agents", agent_id, "routes")
        routes = []
        if not os.path.exists(routes_dir):
            return routes
        for filename in os.listdir(routes_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                with open(os.path.join(routes_dir, filename), "r") as f:
                    route_data = yaml.safe_load(f)
                    if route_data and "route_id" in route_data:
                        routes.append(route_data)
        return routes

    def _llm_classify(self, user_input: str, routes: List[Dict]) -> Tuple[str, float, Dict]:
        routes_desc = "\n".join([f"  - {r['route_id']}: {r.get('description', '')}" for r in routes])
        prompt = f"""Eres un clasificador de intenciones. Tu tarea es elegir la ruta más adecuada para la consulta del usuario.

RUTAS DISPONIBLES (cada una tiene un ID único):
{routes_desc}

CONSULTA DEL USUARIO: "{user_input}"

INSTRUCCIONES ESTRICTAS:
- Responde ÚNICAMENTE con el ID de la ruta elegida (ej: "crear_npc", "trama_principal", etc.).
- No agregues números, comillas, explicaciones ni puntos.
- Si ninguna ruta es claramente adecuada, responde exactamente "RUTA_NO_ENCONTRADA".

TU RESPUESTA (SOLO EL ID):"""
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.0, "num_predict": 20}
                },
                timeout=30
            )
            raw_response = response.json().get("response", "").strip()
            logger.debug(f"Clasificador (raw): '{raw_response}'")
            cleaned = re.sub(r'^[\'"]|[\'"]$', '', raw_response).strip().lower()
            if cleaned.isdigit():
                idx = int(cleaned) - 1
                if 0 <= idx < len(routes):
                    return routes[idx]['route_id'], 1.0, routes[idx]
            for r in routes:
                if r["route_id"].lower() == cleaned:
                    return r["route_id"], 1.0, r
            if "no_encontrada" in cleaned:
                raise ValueError("No match")
            raise ValueError(f"No se pudo interpretar: '{raw_response}'")
        except Exception as e:
            logger.warning(f"Clasificador falló: {e}")
            return None, 0.0, None

    def _fallback_embedding(self, user_input: str, routes: List[Dict]) -> Tuple[str, float, Dict]:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        route_texts = [f"{r['route_id']}: {r.get('description', '')}" for r in routes]
        route_embeds = model.encode(route_texts, convert_to_tensor=True)
        input_embed = model.encode(user_input, convert_to_tensor=True)
        scores = util.cos_sim(input_embed, route_embeds)[0]
        best_idx = int(scores.argmax())
        best_score = float(scores[best_idx])
        best_route = routes[best_idx]
        logger.info(f"Embedding: mejor ruta '{best_route['route_id']}' con score {best_score:.3f}")
        return best_route["route_id"], best_score, best_route

    def needs_rag_context(self, query: str) -> bool:
        return self.rag_guard.needs_rag(query)[0]

    def route(self, agent_id: str, user_input: str, threshold: float = 0.5) -> Tuple[str, float, Dict]:
        routes = self._load_agent_routes(agent_id)
        if not routes:
            raise RouteNotFoundError("No hay rutas definidas para este agente.", [])

        if self.mode == "ollama":
            try:
                route_id, confidence, route_data = self._llm_classify(user_input, routes)
                if route_id:
                    return route_id, confidence, route_data
            except Exception as e:
                logger.warning(f"LLM router falló: {e}")

        route_id, confidence, route_data = self._fallback_embedding(user_input, routes)
        if confidence >= threshold:
            return route_id, confidence, route_data

        formatted_routes = [{"route_id": r["route_id"], "description": r.get("description", "")} for r in routes]
        raise RouteNotFoundError("Ruta No Encontrada", formatted_routes)
