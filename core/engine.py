from typing import Tuple, Dict, Any
from core.logger import logger
from services.intent_router import Router, RouteNotFoundError
from services.input_cleaner import Sanitizer
from orchestration.resource_manager import ResourceScheduler
from security.ingress import IngressFilter
from security.egress import EgressFilter
from security.semantic_output import SemanticOutputFilter
from persistence.cache import ResponseCache

class FerdoNANEngine:
    def __init__(self, ingress: IngressFilter, egress: EgressFilter, semantic: SemanticOutputFilter):
        self.router = Router(mode="ollama")
        self.sanitizer = Sanitizer(enabled=True)
        self.ingress = ingress
        self.egress = egress
        self.semantic = semantic
        self.scheduler = ResourceScheduler()
        self.cache = ResponseCache()
        self.core_config = {}
        self.rag_engine = None  # se inyectará después

    def set_rag_engine(self, rag_engine):
        self.rag_engine = rag_engine
        # Actualizar el router con los dominios del agente
        # (opcional: se puede hacer por agente, queda pendiente)

    def _get_llm_client(self, agent_id: str, manifest_data: dict, core_config: dict):
        from services.llm_providers import OllamaClient, GeminiClient, GroqClient, LocalClient
        provider = manifest_data.get("llm_provider", {}).get("name", "ollama")
        provider_config = manifest_data.get("llm_provider", {})
        # Selección dinámica de perfil de recursos
        if manifest_data.get("llm_provider", {}).get("dynamic_resource_management", False):
            profile = self.scheduler.select_resource_profile(manifest_data.get("llm_provider", {}))
            profile_config = manifest_data.get("llm_provider", {}).get("resource_profiles", {}).get(profile, {})
            if profile_config:
                provider_config.update(profile_config)
                logger.info(f"Perfil dinámico '{profile}' seleccionado para agente {agent_id} (modelo: {provider_config.get('model')})")
        if provider == "ollama":
            return OllamaClient(agent_id, provider_config, core_config)
        elif provider == "gemini":
            if not provider_config.get("api_key") and core_config.get("llm", {}).get("gemini", {}).get("api_key"):
                provider_config["api_key"] = core_config["llm"]["gemini"]["api_key"]
            return GeminiClient(agent_id, provider_config, core_config)
        elif provider == "groq":
            if not provider_config.get("api_key") and core_config.get("llm", {}).get("groq", {}).get("api_key"):
                provider_config["api_key"] = core_config["llm"]["groq"]["api_key"]
            return GroqClient(agent_id, provider_config, core_config)
        else:
            return LocalClient(agent_id, provider_config, core_config)

    def process_pipeline(self, agent_manifest, raw_input: str) -> Tuple[str, Dict[str, Any]]:
        cleaned_input = self.sanitizer.clean(raw_input)
        firewall_override = getattr(agent_manifest, 'firewall_override', {})
        if not self.ingress.evaluate(cleaned_input, firewall_override):
            raise PermissionError("Entrada bloqueada por Firewall Ingress.")

        can_parallel, reason = self.scheduler.can_run_parallel(agent_manifest)
        effective_mode = "parallel" if can_parallel else self.scheduler.suggest_degradation(agent_manifest.id)
        logger.info(f"PIPELINE_START: agent_id={agent_manifest.id}, mode={effective_mode}")

        # Router (obtiene la ruta)
        try:
            route_id, confidence, route_data = self.router.route(agent_manifest.id, cleaned_input)
        except RouteNotFoundError as e:
            logger.warning(f"Router: {str(e)}")
            raise

        # Decidir si añadir contexto RAG
        enhanced_prompt = cleaned_input
        if self.router.needs_rag_context(cleaned_input):
            logger.info(f"RAG activado para consulta: {cleaned_input[:50]}...")
            if self.rag_engine:
                try:
                    context_results = self.rag_engine.rag_query(agent_manifest.id, cleaned_input, top_k=3)
                    if context_results and context_results.get('documents'):
                        context_text = "\n\n".join(context_results['documents'][0])
                        enhanced_prompt = f"Contexto relevante:\n{context_text}\n\nConsulta: {cleaned_input}"
                        logger.info(f"Contexto RAG inyectado ({len(context_text)} caracteres)")
                except Exception as e:
                    logger.warning(f"Error consultando RAG: {e}")
            else:
                logger.warning("RAG Engine no disponible, continuando sin contexto")

        # Verificar caché

        # DEBUG: Verificar caché
        cache_key_debug = f"{agent_manifest.id}|{route_id}|{enhanced_prompt[:50]}"
        print(f"[CACHE DEBUG] Buscando: {cache_key_debug}")
        cached_output = self.cache.get(agent_manifest.id, route_id, enhanced_prompt)
        if cached_output:
            print(f"[CACHE DEBUG] ✅ HIT! Longitud: {len(cached_output)}")
            output = cached_output
        else:
            print(f"[CACHE DEBUG] ❌ MISS")
            # Ejecutar ruta con LLM
            llm = agent_manifest.llm_client
            system_prompt = route_data.get("system_prompt", "Eres un asistente útil.")
            llm_config = route_data.get("model_config", {})
            output = llm.generate_response(enhanced_prompt, system_prompt, llm_config)
            print(f"[CACHE DEBUG] Guardando respuesta...")
            self.cache.set(agent_manifest.id, route_id, enhanced_prompt, output)
        if not self.egress.evaluate(output, route_data):
            return "ERROR_SEGURIDAD_EGRESS", {"status": "blocked", "route_id": route_id}
        output = self.semantic.evaluate_and_replace(output, route_data)

        # Mostrar métricas (opcional)
        import time
        if not hasattr(self, '_last_request_time'):
            self._last_request_time = time.time()
        elapsed = time.time() - self._last_request_time
        self._last_request_time = time.time()
        print(f"[⏱️  Tiempo respuesta: {elapsed:.2f}s]")
        return output, {
            "route_id": route_id,
            "confidence": confidence,
            "execution_mode": effective_mode
        }
