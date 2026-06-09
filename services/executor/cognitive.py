import json
import re
from typing import Dict, Any, Optional
from core.logger import logger
from .base import BaseExecutor

class CognitiveExecutor(BaseExecutor):
    """Ejecuta rutas cognitivas usando el LLM del agente, con soporte para stages multi-LLM."""
    
    def _get_llm_for_stage(self, agent_manifest, stage_config: Dict[str, Any], core_config: Dict[str, Any]):
        """Crea un cliente LLM específico para el stage si tiene provider/model definido."""
        provider = stage_config.get("provider")
        model = stage_config.get("model")
        
        # Si no hay provider específico, usar el LLM por defecto del agente
        if not provider:
            return agent_manifest.llm_client
        
        # Construir configuración para el nuevo cliente
        provider_config = {
            "name": provider,
            "model": model or stage_config.get("model", "llama3.2:3b"),
            "temperature": stage_config.get("temperature", 0.7),
            "max_tokens": stage_config.get("max_tokens", 2048)
        }
        
        # Si el stage tiene API key específica, usarla
        if stage_config.get("api_key"):
            provider_config["api_key"] = stage_config["api_key"]
        
        # Importar los clientes dinámicamente
        from services.llm_providers import OllamaClient, GeminiClient, GroqClient, LocalClient
        
        if provider == "ollama":
            return OllamaClient(agent_manifest.id, provider_config, core_config)
        elif provider == "gemini":
            # Usar API key del stage o del core_config
            if not provider_config.get("api_key") and core_config.get("llm", {}).get("gemini", {}).get("api_key"):
                provider_config["api_key"] = core_config["llm"]["gemini"]["api_key"]
            return GeminiClient(agent_manifest.id, provider_config, core_config)
        elif provider == "groq":
            if not provider_config.get("api_key") and core_config.get("llm", {}).get("groq", {}).get("api_key"):
                provider_config["api_key"] = core_config["llm"]["groq"]["api_key"]
            return GroqClient(agent_manifest.id, provider_config, core_config)
        else:
            logger.warning(f"Provider desconocido '{provider}', usando LLM por defecto")
            return agent_manifest.llm_client
    
    def _validate_stage_output(self, output: str, stage_name: str, output_key: str) -> bool:
        """Valida que la salida de una etapa no esté vacía y tenga contenido útil."""
        if output is None:
            logger.error(f"Stage '{stage_name}' produjo salida None para key '{output_key}'")
            return False
        if not output or not output.strip():
            logger.error(f"Stage '{stage_name}' produjo salida vacía para key '{output_key}'")
            return False
        return True

    def _execute_stage(self, agent_manifest, stage_config: Dict[str, Any], context: Dict[str, str], cleaned_input: str, core_config: Dict[str, Any]) -> tuple[str, Dict[str, str]]:
        """Ejecuta una etapa individual con su propio LLM y actualiza el contexto."""
        # Obtener el LLM adecuado para este stage
        llm = self._get_llm_for_stage(agent_manifest, stage_config, core_config)
        
        prompt_template = stage_config.get("prompt", "{user_input}")
        system_prompt = stage_config.get("system_prompt", "")
        output_key = stage_config.get("output_key", f"stage_{stage_config.get('name', 'output')}")
        timeout = stage_config.get("timeout", getattr(agent_manifest, "execution_timeout", 30))
        
        # Formatear prompt con el contexto actual
        try:
            formatted_prompt = prompt_template.format(**context, user_input=cleaned_input)
        except KeyError as e:
            logger.error(f"Falta clave en contexto para stage '{stage_config.get('name')}': {e}")
            return "", context
        
        # Configurar timeout y otros parámetros
        llm_config = {
            "timeout": timeout,
            "temperature": stage_config.get("temperature", 0.7),
            "max_tokens": stage_config.get("max_tokens", 2048),
            "model": stage_config.get("model", llm.provider_config.get("model", "llama3.2:3b"))
        }
        
        provider_name = stage_config.get("provider", "default")
        logger.info(f"Ejecutando stage '{stage_config.get('name')}' con proveedor: {provider_name}")
        
        try:
            output = llm.generate_response(formatted_prompt, system_prompt, llm_config)
            if self._validate_stage_output(output, stage_config.get('name', 'unnamed'), output_key):
                context[output_key] = output
            else:
                # Si la salida es inválida, reintentar una vez
                logger.warning(f"Stage '{stage_config.get('name')}' output inválido. Reintentando.")
                output = llm.generate_response(formatted_prompt, system_prompt, llm_config)
                if self._validate_stage_output(output, stage_config.get('name', 'unnamed'), output_key):
                    context[output_key] = output
                else:
                    context[output_key] = f"[ERROR: Stage '{stage_config.get('name')}' no produjo salida válida después de reintento]"
            return output, context
        except Exception as e:
            logger.error(f"Error en stage '{stage_config.get('name')}': {e}")
            context[output_key] = f"[ERROR: {str(e)}]"
            return f"Error: {str(e)}", context

    def execute(self, agent_manifest, route_data: Dict[str, Any], cleaned_input: str, router, rag_engine) -> str:
        # Obtener core_config del engine si está disponible
        core_config = getattr(agent_manifest, 'core_config', {})
        if hasattr(agent_manifest, 'llm_client') and hasattr(agent_manifest.llm_client, 'core_config'):
            core_config = agent_manifest.llm_client.core_config
        
        # Si la ruta tiene stages, ejecutar secuencialmente
        stages = route_data.get("stages")
        if stages:
            logger.info(f"Ejecutando ruta con {len(stages)} stages")
            context = {}
            final_output = ""
            for stage in stages:
                stage_name = stage.get("name", "unknown")
                logger.debug(f"Ejecutando stage: {stage_name}")
                output, context = self._execute_stage(agent_manifest, stage, context, cleaned_input, core_config)
                final_output = output  # la última etapa será la respuesta final
            # Si hay una clave de salida específica en la ruta, usarla
            final_key = route_data.get("final_output_key", "respuesta_final")
            if final_key in context:
                return context[final_key]
            return final_output
        
        # Comportamiento original (sin stages)
        enhanced_prompt = cleaned_input
        if router.needs_rag_context(cleaned_input, agent_manifest) and rag_engine:
            try:
                context_results = rag_engine.rag_query(agent_manifest.id, cleaned_input, top_k=3)
                if context_results and context_results.get('documents'):
                    context_text = "\n\n".join(context_results['documents'][0])
                    enhanced_prompt = f"Contexto relevante:\n{context_text}\n\nConsulta: {cleaned_input}"
                    logger.info(f"Contexto RAG inyectado ({len(context_text)} caracteres)")
            except Exception as e:
                logger.warning(f"Error consultando RAG: {e}")
        llm = agent_manifest.llm_client
        system_prompt = route_data.get("system_prompt", "Eres un asistente útil.")
        llm_config = route_data.get("model_config", {})
        # Inyectar timeout desde el agente si no está definido
        if "timeout" not in llm_config:
            llm_config["timeout"] = getattr(agent_manifest, "execution_timeout", 30)
        output = llm.generate_response(enhanced_prompt, system_prompt, llm_config)
        return output

    def _stream_response(self, llm, prompt: str, system_prompt: str, llm_config: dict) -> str:
        """
        Genera respuesta con streaming, mostrando tokens en tiempo real.
        """
        full_response = ""
        try:
            # Forzar stream=True
            llm_config["stream"] = True
            print("\n[🤖 Streaming]: ", end="", flush=True)
            
            # Llamar al método de streaming del LLM
            # El cliente Ollama ya maneja streaming internamente
            response = llm.generate_response(prompt, system_prompt, llm_config)
            
            # Si el cliente ya devuelve la respuesta completa, la mostramos
            # En realidad, necesitamos acceso a los chunks
            # Implementamos streaming manual
            import requests
            import json
            
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": llm_config.get("model", "phi3:mini"),
                "prompt": prompt,
                "system": system_prompt,
                "stream": True,
                "options": {
                    "temperature": llm_config.get("temperature", 0.7),
                    "num_predict": llm_config.get("max_tokens", 2048)
                }
            }
            
            response = requests.post(url, json=payload, stream=True, timeout=llm_config.get("timeout", 30))
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        token = data.get("response", "")
                        if token:
                            print(token, end="", flush=True)
                            full_response += token
                        if data.get("done"):
                            print()  # Nueva línea al final
                            break
                    except:
                        pass
            
            return full_response
        except Exception as e:
            error_msg = f"\n[ERROR] Streaming falló: {e}"
            print(error_msg)
            return error_msg
