import requests
import json
import time
from .base import LLMClient
from core.logger import logger

class OllamaClient(LLMClient):
    def generate_response(self, prompt: str, system_prompt: str, config: dict, stream: bool = True) -> str:
        model = config.get("model", "phi3:mini")
        url = "http://localhost:11434/api/generate"
        timeout = config.get("timeout", 30)
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
        try:
            if stream:
                response = requests.post(url, json=payload, stream=True, timeout=timeout)
                response.raise_for_status()
                full_output = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            token = data.get("response", "")
                            if token:
                                full_output += token
                            if data.get("done"):
                                break
                        except:
                            pass
                return full_output
            else:
                response = requests.post(url, json=payload, timeout=timeout)
                response.raise_for_status()
                data = response.json()
                output = data.get("response", "")
                return output
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(error_msg)
            return error_msg
