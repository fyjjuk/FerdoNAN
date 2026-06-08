import requests
import json
import time
from .base import LLMClient
from core.logger import logger

class OllamaClient(LLMClient):
    def generate_response(self, prompt: str, system_prompt: str, config: dict, stream: bool = False) -> str:
        print(f"[STREAM DEBUG] stream={stream}, prompt={prompt[:50]}...")
        model = config.get("model", "llama3.2:3b")
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": stream,
            "options": {
                "temperature": config.get("temperature", 0.7),
                "num_predict": config.get("max_tokens", 2048)
            }
        }
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                if stream:
                    response = requests.post(url, json=payload, stream=True, timeout=120)
                    response.raise_for_status()
                    full_output = ""
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                token = data.get("response", "")
                                if token:
                                    print(token, end='', flush=True)
                                    full_output += token
                                if data.get("done"):
                                    break
                            except:
                                pass
                    print()
                    ti = len(prompt.split()) + len(system_prompt.split())
                    to = len(full_output.split())
                    self._log_telemetry("ollama", model, ti, to)
                    return full_output
                else:
                    response = requests.post(url, json=payload, timeout=120)
                    response.raise_for_status()
                    data = response.json()
                    output = data.get("response", "")
                    ti = len(prompt.split()) + len(system_prompt.split())
                    to = len(output.split())
                    self._log_telemetry("ollama", model, ti, to)
                    return output
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout en Ollama (intento {attempt+1}/{max_retries+1})")
                if attempt == max_retries:
                    return f"Error: Timeout después de {max_retries+1} intentos"
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error en Ollama: {e}")
                return f"Error: {str(e)}"
        return "Error: No se pudo completar la solicitud"
