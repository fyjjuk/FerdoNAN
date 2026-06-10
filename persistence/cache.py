import hashlib
import json
import os
import time
from core.logger import logger as core_logger
logger = core_logger

class ResponseCache:
    def __init__(self, cache_dir="cache", ttl_seconds=3600):
        self.cache_dir = cache_dir
        self.ttl = ttl_seconds
        os.makedirs(cache_dir, exist_ok=True)

    def _get_key(self, agent_id: str, route_id: str, prompt: str) -> str:
        data = f"{agent_id}|{route_id}|{prompt}"
        return hashlib.md5(data.encode()).hexdigest()

    def get(self, agent_id: str, route_id: str, prompt: str):
        key = self._get_key(agent_id, route_id, prompt)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cached = json.load(f)
            if time.time() - cached['timestamp'] < self.ttl:
                logger.info(f"Cache hit for {agent_id}/{route_id}")
                return cached['response']
            else:
                os.remove(cache_file)
        return None

    def set(self, agent_id: str, route_id: str, prompt: str, response: str):
        key = self._get_key(agent_id, route_id, prompt)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'response': response,
                'agent_id': agent_id,
                'route_id': route_id,
                'prompt_hash': key
            }, f)
        logger.info(f"Cached response for {agent_id}/{route_id}")

    def invalidate(self, agent_id: str, route_id: str = None):
        """Invalida la caché para un agente o ruta específica."""
        count = 0
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
                
            filepath = os.path.join(self.cache_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                if route_id:
                    # Invalida ruta específica
                    if data.get('agent_id') == agent_id and data.get('route_id') == route_id:
                        os.remove(filepath)
                        count += 1
                        logger.info(f"Cache invalidated for {agent_id}/{route_id}")
                else:
                    # Invalida todo el agente
                    if data.get('agent_id') == agent_id:
                        os.remove(filepath)
                        count += 1
            except (json.JSONDecodeError, KeyError, OSError):
                # Archivo corrupto, eliminarlo
                os.remove(filepath)
                count += 1
        
        if count > 0:
            logger.info(f"Cache invalidated for agent {agent_id}: {count} entries removed")
        else:
            logger.info(f"No cache entries found for agent {agent_id}")
