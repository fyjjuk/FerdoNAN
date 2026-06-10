"""
Cognitive Executor - Ejecución de rutas con stages y soporte de streaming
"""

import logging
from typing import Dict, Any

from .stage_runner import StageRunner
from .streaming import StreamHandler

logger = logging.getLogger(__name__)


class CognitiveExecutor:
    """Ejecutor cognitivo para rutas con stages y streaming"""
    
    def __init__(self, agent_manifest):
        """Inicializa el ejecutor con el manifiesto del agente"""
        self.agent_manifest = agent_manifest
        self.stage_runner = StageRunner(agent_manifest)
    
    def execute(self, agent_manifest, route_data: Dict[str, Any], 
                cleaned_input: str, router, rag_engine) -> str:
        """
        Ejecuta una ruta, ya sea con stages o simple
        
        Args:
            agent_manifest: Manifiesto del agente
            route_data: Datos de la ruta a ejecutar
            cleaned_input: Input sanitizado del usuario
            router: Router para determinar necesidades
            rag_engine: Motor RAG para contexto
            
        Returns:
            str: Respuesta generada
        """
        # Obtener core_config del engine si está disponible
        core_config = getattr(agent_manifest, 'core_config', {})
        if hasattr(agent_manifest, 'llm_client') and hasattr(agent_manifest.llm_client, 'core_config'):
            core_config = agent_manifest.llm_client.core_config
        
        # Verificar si la ruta tiene stages
        stages = route_data.get("stages")
        if stages:
            logger.info(f"Ejecutando ruta con {len(stages)} stages")
            context = {}
            final_output = ""
            
            for stage in stages:
                stage_name = stage.get("name", "unknown")
                logger.debug(f"Ejecutando stage: {stage_name}")
                output, context = self.stage_runner.execute_stage(
                    stage, context, cleaned_input, core_config
                )
                final_output = output  # la última etapa será la respuesta final
            
            # Si hay una clave de salida específica en la ruta, usarla
            final_key = route_data.get("final_output_key", "respuesta_final")
            if final_key in context:
                return context[final_key]
            return final_output
        
        # Comportamiento original (sin stages)
        enhanced_prompt = cleaned_input
        
        # Inyectar contexto RAG si es necesario
        if router.needs_rag_context(cleaned_input, agent_manifest) and rag_engine:
            try:
                context_results = rag_engine.rag_query(agent_manifest.id, cleaned_input, top_k=3)
                if context_results and context_results.get('documents'):
                    context_text = "\n\n".join(context_results['documents'][0])
                    enhanced_prompt = f"Contexto relevante:\n{context_text}\n\nConsulta: {cleaned_input}"
                    logger.info(f"Contexto RAG inyectado ({len(context_text)} caracteres)")
            except Exception as e:
                logger.warning(f"Error consultando RAG: {e}")
        
        # Obtener LLM y configurar
        llm = agent_manifest.llm_client
        system_prompt = route_data.get("system_prompt", "Eres un asistente útil.")
        llm_config = route_data.get("model_config", {})
        
        # Inyectar timeout desde el agente si no está definido
        if "timeout" not in llm_config:
            llm_config["timeout"] = getattr(agent_manifest, "execution_timeout", 30)
        
        # Verificar si se debe usar streaming
        use_streaming = llm_config.get("stream", False)
        
        if use_streaming and hasattr(llm, 'stream_response'):
            logger.info("Usando streaming para la respuesta")
            response = ""
            for token in StreamHandler.stream_with_yield(llm, enhanced_prompt, system_prompt, llm_config):
                response += token
            return response
        else:
            # Streaming no disponible o desactivado, usar método normal
            output = llm.generate_response(enhanced_prompt, system_prompt, llm_config)
            return output
    
    def _stream_response(self, llm, prompt: str, system_prompt: str, llm_config: dict) -> str:
        """
        Método legacy para compatibilidad
        """
        return StreamHandler.stream_response_legacy(llm, prompt, system_prompt, llm_config)
