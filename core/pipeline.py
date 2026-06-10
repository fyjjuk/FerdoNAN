from typing import Tuple, Dict, Any
from core.logger import logger
from core.factory import create_router, create_sanitizer
from services.router.intent_router import RouteNotFoundError
from config.settings import settings

def run_pipeline(agent_manifest, raw_input: str, 
                 ingress, egress, semantic, 
                 gatekeeper, cache, rag_engine,
                 core_config: dict) -> Tuple[str, Dict[str, Any]]:
    """
    Ejecuta el pipeline completo de procesamiento:
    1. Sanitiza el input
    2. Valida con firewall Ingress
    3. Enruta la consulta
    4. Opcionalmente verifica con Gatekeeper
    5. Ejecuta la ruta (con caché)
    6. Valida con firewall Egress
    7. Filtra salida semántica
    """
    router = create_router(agent_manifest)
    sanitizer = create_sanitizer(agent_manifest)

    cleaned_input = sanitizer.clean(raw_input)
    if not ingress.evaluate(cleaned_input, agent_manifest):
        raise PermissionError("Entrada bloqueada por Firewall Ingress.")

    # Nota: El ResourceScheduler se instancia dentro del engine, 
    # pero por ahora lo creamos aquí para no romper dependencias
    from orchestration.resource_manager import ResourceScheduler
    scheduler = ResourceScheduler()
    
    can_parallel, reason = scheduler.can_run_parallel(agent_manifest)
    effective_mode = "parallel" if can_parallel else scheduler.suggest_degradation(agent_manifest.id)
    logger.info(f"PIPELINE_START: agent_id={agent_manifest.id}, mode={effective_mode}")

    try:
        route_id, confidence, route_data = router.route(agent_manifest.id, cleaned_input)
    except RouteNotFoundError as e:
        logger.warning(f"Router: {str(e)}")
        raise

    gatekeeper_required = route_data.get("gatekeeper_required", False)
    force_gatekeeper = core_config.get("pipeline", {}).get("gatekeeper", {}).get("force_for_all_routes", settings.GATEKEEPER_FORCE_ALL)
    
    if gatekeeper_required or force_gatekeeper:
        from security.auth.gatekeeper import Gatekeeper
        from core.tracing import get_request_id
        timeout = core_config.get("pipeline", {}).get("gatekeeper", {}).get("default_timeout_seconds", settings.GATEKEEPER_TIMEOUT)
        gk = gatekeeper if gatekeeper is not None else Gatekeeper(default_timeout=timeout, force_all=force_gatekeeper)
        request_id = get_request_id() or "unknown"
        if not gk.verify(route_id, route_data, request_id):
            raise PermissionError(f"Acción rechazada por Gatekeeper. Ruta: {route_id}")

    cached_output = cache.get(agent_manifest.id, route_id, cleaned_input)
    if cached_output:
        output = cached_output
    else:
        from services.executor.factory import create_executor
        executor = create_executor(route_data)
        output = executor.execute(agent_manifest, route_data, cleaned_input, router, rag_engine)
        cache.set(agent_manifest.id, route_id, cleaned_input, output)

    if not egress.evaluate(output, route_data):
        return "ERROR_SEGURIDAD_EGRESS", {"status": "blocked", "route_id": route_id}
    output = semantic.evaluate_and_replace(output, route_data)

    return output, {
        "route_id": route_id,
        "confidence": confidence,
        "execution_mode": effective_mode
    }
