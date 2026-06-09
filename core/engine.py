from typing import Tuple, Dict, Any
import subprocess
import json
import os
import re
import shutil
from core.logger import logger
from services.intent_router import Router, RouteNotFoundError
from services.input_cleaner import Sanitizer
from orchestration.resource_manager import ResourceScheduler
from security.ingress import IngressFilter
from security.egress import EgressFilter
from security.semantic_output import SemanticOutputFilter
from persistence.cache import ResponseCache

class FerdoNANEngine:
    def __init__(self, ingress: IngressFilter, egress: EgressFilter, semantic: SemanticOutputFilter,
                 gatekeeper=None, cache=None, rag_engine=None):
        self.ingress = ingress
        self.egress = egress
        self.semantic = semantic
        self.scheduler = ResourceScheduler()
        self.cache = cache if cache is not None else ResponseCache()
        self.gatekeeper = gatekeeper  # puede ser None, se creará bajo demanda si es necesario
        self.core_config = {}
        self.rag_engine = rag_engine

    def set_rag_engine(self, rag_engine):
        self.rag_engine = rag_engine

    def _get_llm_client(self, agent_id: str, manifest_data: dict, core_config: dict):
        from services.llm_providers import OllamaClient, GeminiClient, GroqClient, LocalClient
        provider = manifest_data.get("llm_provider", {}).get("name", "ollama")
        provider_config = manifest_data.get("llm_provider", {})
        if manifest_data.get("llm_provider", {}).get("dynamic_resource_management", False):
            profile = self.scheduler.select_resource_profile(manifest_data.get("llm_provider", {}))
            profile_config = manifest_data.get("llm_provider", {}).get("resource_profiles", {}).get(profile, {})
            if profile_config:
                provider_config.update(profile_config)
                logger.info(f"Perfil dinámico '{profile}' seleccionado para agente {agent_id}")
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

    def _create_router(self, agent_manifest):
        cfg = agent_manifest.router_config
        return Router(mode=cfg.mode, model=cfg.model, threshold=cfg.threshold)

    def _create_sanitizer(self, agent_manifest):
        cfg = agent_manifest.sanitizer_config
        return Sanitizer(enabled=cfg.enabled, model=cfg.model)

    def process_pipeline(self, agent_manifest, raw_input: str) -> Tuple[str, Dict[str, Any]]:
        router = self._create_router(agent_manifest)
        sanitizer = self._create_sanitizer(agent_manifest)

        cleaned_input = sanitizer.clean(raw_input)
        if not self.ingress.evaluate(cleaned_input, agent_manifest):
            raise PermissionError("Entrada bloqueada por Firewall Ingress.")

        can_parallel, reason = self.scheduler.can_run_parallel(agent_manifest)
        effective_mode = "parallel" if can_parallel else self.scheduler.suggest_degradation(agent_manifest.id)
        logger.info(f"PIPELINE_START: agent_id={agent_manifest.id}, mode={effective_mode}")

        try:
            route_id, confidence, route_data = router.route(agent_manifest.id, cleaned_input)
        except RouteNotFoundError as e:
            logger.warning(f"Router: {str(e)}")
            raise

        # === GATEKEEPER: Verificación humana para rutas críticas ===
        gatekeeper_required = route_data.get("gatekeeper_required", False)
        force_gatekeeper = self.core_config.get("pipeline", {}).get("gatekeeper", {}).get("force_for_all_routes", False)
        
        if gatekeeper_required or force_gatekeeper:
            from security.gatekeeper import Gatekeeper
            from core.tracing import get_request_id
            timeout = self.core_config.get("pipeline", {}).get("gatekeeper", {}).get("default_timeout_seconds", 60)
            # Usar gatekeeper inyectado o crear uno por defecto
            gk = self.gatekeeper if self.gatekeeper is not None else Gatekeeper(default_timeout=timeout, force_all=force_gatekeeper)
            request_id = get_request_id() or "unknown"
            if not gk.verify(route_id, route_data, request_id):
                raise PermissionError(f"Acción rechazada por Gatekeeper. Ruta: {route_id}")
        # === FIN GATEKEEPER ===

        cached_output = self.cache.get(agent_manifest.id, route_id, cleaned_input)
        if cached_output:
            output = cached_output
        else:
            from services.executor.factory import create_executor
            executor = create_executor(route_data)
            output = executor.execute(agent_manifest, route_data, cleaned_input, router, self.rag_engine)
            self.cache.set(agent_manifest.id, route_id, cleaned_input, output)

        if not self.egress.evaluate(output, route_data):
            return "ERROR_SEGURIDAD_EGRESS", {"status": "blocked", "route_id": route_id}
        output = self.semantic.evaluate_and_replace(output, route_data)

        return output, {
            "route_id": route_id,
            "confidence": confidence,
            "execution_mode": effective_mode
        }
