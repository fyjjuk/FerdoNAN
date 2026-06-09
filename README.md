# FerdoNAN - Asistente Personal con Agentes Especializados

**Versión:** 2.0 (Modular con Stages y Perfiles Dinámicos)
**Estado:** Producción estable

## Descripción General

FerdoNAN es un asistente personal basado en agentes especializados, cada uno con su propio modelo de lenguaje, configuración de seguridad y capacidades. Soporta múltiples proveedores LLM (Ollama local, Gemini, Groq), sistema de stages (encadenamiento de LLMs), caché de respuestas, firewall multicapa y gestión dinámica de recursos.

## Estructura del Proyecto

```
ferdonan/
├── agents/              # Agentes especializados (cada uno con config.yaml y routes/)
├── core/                # Motor principal (engine, logger, tracing)
├── services/            # LLM providers, sanitizador, router, RAG, MCP client
├── security/            # Firewalls (ingress, egress, semántico) y gatekeeper
├── orchestration/       # Gestor de recursos (paralelismo, perfiles dinámicos)
├── persistence/         # Memoria a corto plazo, backups, caché de respuestas
├── models/              # Modelos de datos (manifest)
├── scripts/             # Utilidades de usuario y diagnóstico
├── tests/               # Pruebas unitarias
├── ui/                  # Selector interactivo de agentes
└── tools/               # Herramientas nativas (web_search, spotify_control, etc.)
```

## Características Principales

### 1. Agentes Especializados
Cada agente tiene:
- Configuración independiente (`config.yaml`)
- Rutas específicas (`routes/*.yaml`) con descripciones semánticas
- Memoria a corto plazo por agente
- RAG opcional con documentos locales

### 2. Múltiples Proveedores LLM
- **Ollama** (local: llama3.2, phi4-mini, qwen2.5)
- **Gemini** (API)
- **Groq** (API)
- Cliente mock para pruebas

### 3. Sistema de Stages (Encadenamiento de LLMs)
Permite ejecutar múltiples LLMs en secuencia, pasando resultados entre etapas:

```yaml
stages:
  - name: "extraer"
    provider: "ollama"
    model: "phi4-mini"
    prompt: "Extrae datos: {user_input}"
    output_key: "datos"
  - name: "formatear"
    provider: "gemini"
    prompt: "Formatea: {datos}"
    output_key: "respuesta"
```

### 4. Perfiles Dinámicos de Recursos
El sistema selecciona automáticamente el modelo según RAM/VRAM disponible:

```yaml
llm_provider:
  dynamic_resource_management: true
  resource_profiles:
    high:   { model: "qwen2.5:7b", temperature: 0.8 }
    medium: { model: "llama3.2:3b", temperature: 0.8 }
    low:    { model: "phi4-mini", temperature: 0.5 }
```

### 5. Caché de Respuestas
- Almacenamiento en disco (`cache/`)
- TTL configurable (1 hora por defecto)
- Identificación por agente, ruta y prompt normalizado
- Reduce latencia y consumo de recursos

### 6. Firewall Multicapa
- **Ingress:** Capa1 (regex) y Capa2 (semántica, opcional)
- **Egress:** Filtrado de comandos peligrosos en salidas
- **Semántico:** Detección de contenido inapropiado (toxic-bert)
- **Gatekeeper:** Aprobación humana para rutas críticas

### 7. RAG (Retrieval-Augmented Generation)
- Indexación automática de `docs/` por agente
- Búsqueda semántica con ChromaDB y sentence-transformers
- Inyección de contexto en consultas relevantes

### 8. Telemetría y Logs
- Logs en formato JSON con rotación
- Métricas de tokens por consulta
- Trazabilidad con `request_id`
- Comando para ver logs en tiempo real: `python scripts/user/logs_tail.py`

## Instalación y Configuración

### Requisitos
- Python 3.14+
- Ollama (con modelos descargados)
- (Opcional) API keys de Gemini/Groq

### Instalación
```bash
git clone <repo>
cd ferdonan
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuración
1. Copia `config/core.yaml.example` a `config/core.yaml` (si no existe)
2. Añade API keys de Gemini/Groq si las usas
3. Asegura que Ollama esté corriendo: `ollama serve`

## Uso

### Ejecutar el asistente
```bash
python main.py
```

### Seleccionar agente
El menú mostrará los agentes disponibles. Selecciona por número.

### Comandos útiles
- `salir` - Termina la sesión
- `Ctrl+C` - Interrupción forzada

## Utilidades

```bash
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
```

## Tests

```bash
pytest tests/ -v
```

## Próximos Pasos Planeados

- [ ] Autoregeneración (reintentos con backoff exponencial)
- [ ] Dashboard web con FastAPI
- [ ] Streaming de respuestas (en progreso)
- [ ] Más tests de integración

## Licencia

MIT
