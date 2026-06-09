# FerdoNAN - Asistente Personal con Agentes Especializados

**Versión:** 2.3.0 (Dashboard, Métricas, Streaming, Memoria Larga Plazo, Biblioteca de Rutas)
**Estado:** Producción estable

## Descripción General
FerdoNAN es un asistente personal basado en agentes especializados, cada uno con su propio modelo de lenguaje, configuración de seguridad y capacidades. Soporta múltiples proveedores LLM (Ollama local, Gemini, Groq), sistema de stages (encadenamiento de LLMs), caché de respuestas, firewall multicapa y gestión dinámica de recursos. Incluye dashboard web con métricas Prometheus, memoria a largo plazo, streaming de respuestas y una biblioteca de rutas reutilizables.

## 🚀 Demo con Docker (recomendada)
La forma más rápida de probar FerdoNAN sin instalar dependencias localmente.

### Requisitos
- Docker y Docker Compose instalados.

### Pasos
1. Clona el repositorio:
   git clone https://github.com/fyjjuk/FerdoNAN
   cd FerdoNAN

2. Ejecuta la demo:
   docker-compose -f docker-compose.demo.yml up

3. En otra terminal, descarga los modelos necesarios (solo la primera vez):
   docker exec -it ferdonan-ollama ollama pull phi3:mini
   docker exec -it ferdonan-ollama ollama pull llama3.2:3b

4. Una vez que la aplicación esté corriendo, accede al menú interactivo en la terminal donde se ejecutó docker-compose up.
5. (Opcional) Abre el dashboard en http://localhost:8000
6. Para detenerlo: Ctrl+C y luego docker-compose down.

## 📦 Estructura del Proyecto
ferdonan/
├── agents/              # Agentes especializados (cada uno con config.yaml y routes/)
├── core/                # Motor principal (engine, logger, tracing)
├── services/            # LLM providers, sanitizador, router, RAG, MCP client
├── security/            # Firewalls (ingress, egress, semántico) y gatekeeper
├── orchestration/       # Gestor de recursos (paralelismo, perfiles dinámicos)
├── persistence/         # Memoria a corto y largo plazo, backups, caché de respuestas
├── models/              # Modelos de datos (manifest, route_models)
├── scripts/             # Utilidades de usuario y diagnóstico
├── tests/               # Pruebas unitarias
├── ui/                  # Selector interactivo de agentes
├── tools/               # Herramientas nativas (web_search, spotify_control, etc.)
├── web/                 # Dashboard web (FastAPI, WebSockets)
├── monitoring/          # Métricas Prometheus
└── route_library/       # Biblioteca de rutas de ejemplo (reutilizables)

## ✨ Características Principales
1. Agentes Especializados: Configuración independiente, rutas específicas, memoria a corto/largo plazo, validación Pydantic.
2. Múltiples Proveedores LLM: Ollama, Gemini, Groq.
3. Sistema de Stages: Encadenamiento de LLMs.
4. Perfiles Dinámicos de Recursos: Selección de modelo según hardware.
5. Caché de Respuestas: TTL configurable.
6. Firewall Multicapa: Ingress (regex/semántico), Egress, Gatekeeper.
7. RAG: Indexación y búsqueda semántica.
8. Telemetría y Logs: JSON, rotación, trazabilidad.
9. Dashboard Web: FastAPI, WebSockets.
10. Métricas Prometheus: Endpoint /metrics.
11. Streaming de Respuestas: Tiempo real.
12. Biblioteca de Rutas: Carpeta route_library/ reutilizable.

## 🔧 Instalación y Configuración
### Requisitos
- Python 3.14+
- Ollama (con modelos descargados)
- (Opcional) API keys de Gemini/Groq
- (Opcional) Docker

### Instalación Local
git clone https://github.com/fyjjuk/FerdoNAN
cd FerdoNAN
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### Configuración
- Copia .env.example a .env y edita las API keys.
- Asegura que Ollama esté corriendo: ollama serve

## 🎮 Uso
### Ejecutar el asistente
python main.py

### Dashboard Web
python web/dashboard.py
Accede a http://localhost:8000

### Utilidades
# Backup del proyecto
python scripts/user/backup_cli.py crear
# Ver logs en tiempo real
python scripts/user/logs_tail.py
# Health check
python scripts/diagnostic/check_health.py
# Buscar archivos duplicados
python scripts/diagnostic/find_duplicates.py
# Exportar estructura del proyecto
python scripts/diagnostic/audit_project.py

## 📚 Biblioteca de Rutas
Para copiar una ruta a un agente existente:
./scripts/user/copy_route.sh <nombre_ruta> <id_agente>

## 🧪 Tests
pytest tests/ -v

## 📜 Licencia
MIT

## 🤝 Contribuciones
Por favor, abre un issue o pull request en GitHub.

## 🌟 Próximos Pasos Planeados
- Autoregeneración (reintentos con backoff exponencial)
- Tests de integración
- Mejoras en la interfaz web
- Soporte para más proveedores LLM
