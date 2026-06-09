"""Métricas Prometheus para FerdoNAN."""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import time
from functools import wraps
from typing import Callable, Any

# Contadores
requests_total = Counter(
    'ferdonan_requests_total',
    'Total de solicitudes procesadas',
    ['agent_id', 'route_id', 'status']
)

errors_total = Counter(
    'ferdonan_errors_total',
    'Total de errores por tipo',
    ['agent_id', 'error_type']
)

tokens_consumed = Counter(
    'ferdonan_tokens_consumed_total',
    'Total de tokens consumidos',
    ['agent_id', 'provider', 'model']
)

# Histogramas
latency_seconds = Histogram(
    'ferdonan_request_duration_seconds',
    'Duración de solicitudes en segundos',
    ['agent_id', 'route_id'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0)
)

tokens_per_request = Histogram(
    'ferdonan_tokens_per_request',
    'Tokens por solicitud',
    ['agent_id', 'provider'],
    buckets=(50, 100, 200, 500, 1000, 2000, 5000)
)

# Gauges (valores actuales)
active_agents = Gauge('ferdonan_active_agents', 'Número de agentes activos')
ollama_status = Gauge('ferdonan_ollama_status', 'Estado de Ollama (1=up, 0=down)')
memory_usage_mb = Gauge('ferdonan_memory_usage_mb', 'Uso de memoria en MB')
cpu_usage_percent = Gauge('ferdonan_cpu_usage_percent', 'Uso de CPU porcentaje')

def track_request(agent_id: str, route_id: str):
    """Decorador para trackear métricas de solicitud."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                latency = time.time() - start_time
                latency_seconds.labels(agent_id=agent_id, route_id=route_id).observe(latency)
                requests_total.labels(agent_id=agent_id, route_id=route_id, status='success').inc()
                return result
            except Exception as e:
                requests_total.labels(agent_id=agent_id, route_id=route_id, status='error').inc()
                errors_total.labels(agent_id=agent_id, error_type=type(e).__name__).inc()
                raise
        return wrapper
    return decorator

def record_tokens(agent_id: str, provider: str, model: str, input_tokens: int, output_tokens: int):
    """Registra consumo de tokens."""
    total = input_tokens + output_tokens
    tokens_consumed.labels(agent_id=agent_id, provider=provider, model=model).inc(total)
    tokens_per_request.labels(agent_id=agent_id, provider=provider).observe(total)

def update_system_metrics():
    """Actualiza métricas del sistema."""
    import psutil
    memory_usage_mb.set(psutil.virtual_memory().used / (1024 * 1024))
    cpu_usage_percent.set(psutil.cpu_percent(interval=0.1))

def update_ollama_metric():
    """Actualiza estado de Ollama."""
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True, timeout=2
        )
        ollama_status.set(1 if result.returncode == 0 else 0)
    except:
        ollama_status.set(0)

def get_metrics():
    """Retorna métricas en formato Prometheus."""
    update_system_metrics()
    update_ollama_metric()
    return generate_latest(REGISTRY)
