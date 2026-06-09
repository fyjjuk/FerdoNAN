# Arquitectura de FerdoNAN

## Flujo de procesamiento

Input -> Ingress -> Router -> Agente -> Stages -> LLM -> Egress -> Output

## Componentes

| Directorio | Funcion |
|------------|---------|
| agents/ | Agentes especializados |
| core/ | Motor principal |
| security/ | Firewall + Gatekeeper |
| services/ | LLM providers + RAG |
| persistence/ | Memoria + Cache |
| web/ | Dashboard FastAPI |
| monitoring/ | Metricas Prometheus |
