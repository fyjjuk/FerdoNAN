# FerdoNAN - Asistente Personal con Agentes Especializados

**Versión:** 2.4.0 (Refactorización arquitectónica, RAG modular, tests unitarios)
**Estado:** Producción estable

## Descripción General
FerdoNAN es un asistente personal basado en agentes especializados, cada uno con su propio modelo de lenguaje, configuración de seguridad y capacidades. Soporta múltiples proveedores LLM (Ollama local, Gemini, Groq), sistema de stages (encadenamiento de LLMs), caché de respuestas, firewall multicapa y gestión dinámica de recursos. Incluye dashboard web con métricas Prometheus, memoria a largo plazo, streaming de respuestas y una biblioteca de rutas reutilizables.

## 🚀 Demo con Docker (recomendada)
La forma más rápida de probar FerdoNAN sin instalar dependencias localmente.

### Requisitos
- Docker y Docker Compose instalados.

### Pasos
1. Clona el repositorio:
```bash
   git clone https://github.com/fyjjuk/FerdoNAN
   cd FerdoNAN
```
2. Ejecuta la demo:
```bash
   docker-compose -f docker-compose.demo.yml up
```
3. En otra terminal, descarga los modelos necesarios (solo la primera vez):
```bash
   docker exec -it ferdonan-ollama ollama pull phi3:mini
   docker exec -it ferdonan-ollama ollama pull llama3.2:3b
```
4. Una vez que la aplicación esté corriendo, accede al menú interactivo en la terminal donde se ejecutó `docker-compose up`.
5. (Opcional) Abre el dashboard en http://localhost:8000
6. Para detenerlo: `Ctrl+C` y luego `docker-compose down`.

## 📦 Estructura del Proyecto (Refactorizada v2.4)
```text
ferdonan/
├── agents/              # Agentes especializados (cada uno con config.yaml y routes/)
├── core/                # Motor principal (modularizado)
│   ├── engine.py        # Estado e inicialización (35L)
│   ├── pipeline.py      # Lógica del pipeline de procesamiento
│   ├── factory.py       # Creación de router y sanitizer
│   └── llm_factory.py   # Creación de clientes LLM
├── security/            # Firewalls y seguridad (organizado por capas)
│   ├── filters/         # Ingress, egress, semantic
│   ├── auth/            # Gatekeeper, audit
│   └── rate_limiter.py
├── services/            # Servicios core (modularizados)
│   ├── executor/        # Ejecutores de rutas
│   │   ├── cognitive.py # Orquestación (95L)
│   │   ├── stage_runner.py
│   │   ├── streaming.py
│   │   └── ...
│   ├── router/          # Enrutamiento de intenciones
│   ├── sanitizer/       # Limpieza de inputs
│   ├── llm_providers/   # Clientes LLM (Ollama, Gemini, Groq, Local)
│   └── rag/             # RAG modularizado (NUEVO)
│       ├── __init__.py  # RAGEngine (compatibilidad)
│       ├── utils.py     # Validación y utilidades
│       ├── collection.py # Manejo de ChromaDB
│       ├── indexing.py   # Indexación de documentos
│       └── query.py      # Búsqueda semántica
├── models/              # Modelos de datos Pydantic
├── tests/               # Pruebas unitarias (34+ tests)
├── tools/               # Herramientas nativas
├── orchestration/       # Gestor de recursos
├── persistence/         # Memoria y caché
├── web/                 # Dashboard web
├── monitoring/          # Métricas Prometheus
└── route_library/       # Biblioteca de rutas reutilizables
```

## ✨ Características Principales
- **Agentes Especializados:** Configuración independiente, rutas específicas, memoria a corto/largo plazo
- **Múltiples Proveedores LLM:** Ollama, Gemini, Groq
- **Sistema de Stages:** Encadenamiento de LLMs con soporte multi-proveedor
- **Arquitectura Modular:** SRP aplicado, bajo acoplamiento, alta cohesión
- **RAG Modular:** Indexación y búsqueda semántica con ChromaDB
- **Firewall Multicapa:** Ingress (regex), Egress (comandos peligrosos), Gatekeeper (aprobación humana)
- **Streaming de Respuestas:** Tiempo real con fallback automático
- **Caché de Respuestas:** TTL configurable
- **Dashboard Web:** FastAPI + WebSockets
- **Métricas Prometheus:** Endpoint /metrics
- **Tests Unitarios:** 34+ tests para módulos core

## 🔧 Instalación y Configuración

### Requisitos
- Python 3.14+
- Ollama (con modelos descargados)
- (Opcional) API keys de Gemini/Groq

### Instalación Local
```bash
git clone https://github.com/fyjjuk/FerdoNAN
cd FerdoNAN
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuración
- Copia `.env.example` a `.env` y edita las API keys
- Asegura que Ollama esté corriendo: `ollama serve`

## 🎮 Uso

### Ejecutar el asistente
```bash
python main.py
```

### Dashboard Web
```bash
python web/dashboard.py
# Accede a http://localhost:8000
```

### Ejecutar Tests
```bash
pytest tests/ -v
```

## 🧪 Tests Unitarios
La refactorización incluye 34 tests unitarios que cubren:
- `core/llm_factory.py` - Creación de clientes LLM
- `core/factory.py` - Creación de router y sanitizer
- `core/pipeline.py` - Pipeline de procesamiento
- `executor/stage_runner.py` - Ejecución de stages
- `executor/streaming.py` - Streaming de respuestas
- `rag/` - Servicios RAG modularizados

## 📚 Biblioteca de Rutas
Para copiar una ruta a un agente existente:
```bash
./scripts/user/copy_route.sh <nombre_ruta> <id_agente>
```

## 🔄 Cambios en v2.4 (Refactorización)

### Mejoras arquitectónicas
- Descomposición de `core/engine.py`: 114 → 35 líneas
- Descomposición de `cognitive.py`: 194 → 95 líneas
- Extracción de RAG: 129 líneas → 5 módulos cohesivos
- Reorganización de `security/`: filtros y autenticación separados
- Reorganización de `services/`: router, sanitizer, executor organizados por dominio

### Eliminación de código muerto
- 16 archivos obsoletos eliminados (backups, `.gatekeeper_backup`)

## 📜 Licencia
MIT

## 🤝 Contribuciones
Por favor, abre un issue o pull request en GitHub.

## 🙏 Agradecimientos
- [Repomix](https://github.com/yamadashy/repomix) - Empaquetado eficiente del código para IA
- [ChromaDB](https://www.trychroma.com/) - Base de datos vectorial
- [Sentence Transformers](https://www.sbert.net/) - Embeddings semánticos
