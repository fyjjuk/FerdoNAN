# FerdoNAN - Asistente Personal Multi-Agente con IA

**Versión:** 2.4.0 (Expansión UI, RAG avanzado, CLI mejorado, Ascii-Studio)  
**Estado:** Producción estable | **Arquitectura:** Hexagonal + Plugins

## Descripción General

FerdoNAN es un framework modular para asistentes de IA basado en agentes especializados, diseñado bajo principios de **bajo acoplamiento** y **alta cohesión**. Cada agente opera con su propio modelo de lenguaje, configuración de seguridad y capacidades, mientras que el núcleo (`core/`) proporciona servicios de orquestación, enrutamiento, ejecución y seguridad multicapa.

**Novedades v2.4.0:** Sistema completo de theming visual, CLI con comandos slash y autocompletado, componentes ASCII art, agente de desarrollo (GitHub + code review), y parsing avanzado de documentos con MarkItDown.

## Arquitectura de Alto Nivel

~~~mermaid
flowchart LR
    CLI[CLI Interface] --> ENGINE[FerdoNANEngine]
    ENGINE --> PIPELINE[Pipeline Processor]
    PIPELINE --> ROUTER[Intent Router]
    PIPELINE --> EXECUTOR[Executor Registry]
    EXECUTOR --> LLM[LLM Providers]
    EXECUTOR --> RAG[RAG Engine]
    ENGINE --> INGRESS[Ingress Filter]
    ENGINE --> EGRESS[Egress Filter]
    ENGINE --> GATEKEEPER[Gatekeeper]
    ROUTER --> AGENTS[Specialized Agents]
    RAG --> MARKITDOWN[MarkItDown Parser]
    CLI --> THEMES[UI Themes]
    CLI --> ASCII[ASCII Studio]
~~~

## 📦 Estructura del Proyecto (Refactorizada v2.4)

~~~text
ferdonan/
├── agents/                     # Agentes especializados
│   ├── buscador_web/           # Búsqueda web (DuckDuckGo)
│   ├── experto_linux/          # Administración Linux Fedora
│   ├── narrador_dnd/           # Generador de contenido D&D
│   ├── spotify_player/         # Control de Spotify
│   ├── stage_sandbox/          # Sandbox para pruebas
│   └── dev_assistant/          # Asistente de desarrollo (GitHub, code review)
├── core/                       # Motor principal (modularizado, 35L)
│   ├── engine.py               # Estado e inicialización
│   ├── pipeline.py             # Pipeline de procesamiento
│   ├── factory.py              # Creación de componentes
│   ├── llm_factory.py          # Creación de clientes LLM
│   ├── interfaces.py           # Protocolos y ABCs estandarizados
│   └── i18n/                   # Sistema de localización (JSON)
├── security/                   # Firewalls y seguridad
│   ├── filters/                # Ingress, egress, semantic
│   ├── auth/                   # Gatekeeper, audit
│   └── rate_limiter.py
├── services/                   # Servicios core
│   ├── executor/               # Ejecutores (cognitive, script, stage_runner)
│   ├── router/                 # Enrutamiento (keyword, embedding, hybrid, LLM)
│   ├── sanitizer/              # Limpieza de inputs
│   ├── llm_providers/          # Ollama, Gemini, Groq, Local
│   └── rag/                    # RAG modular
│       ├── parsers/            # MarkItDown adapter (PDF, DOCX, XLSX, PPTX, images)
│       ├── indexing.py         # Indexación con fallback
│       ├── query.py            # Búsqueda semántica
│       └── collection.py       # Gestión de ChromaDB
├── ui/                         # Interfaz de usuario (NUEVO)
│   ├── console/                # Renderer con temas ANSI
│   ├── cli/                    # Comandos slash, historial, autocompletado
│   ├── ascii/                  # Banners, boxes, tables, spinners
│   └── themes/                 # Temas YAML (refero, cyberpunk)
├── models/                     # Modelos de datos Pydantic
├── tests/                      # Pruebas unitarias (44+ tests)
├── tools/native/               # Herramientas nativas
├── locales/                    # Diccionarios i18n (en, es)
├── experimental/               # Código en desarrollo (mcp_client)
└── docs/                       # Documentación Sphinx
~~~

## ✨ Características Principales (Actualizadas)

### Núcleo y Agentes
- **Agentes especializados:** Configuración vía YAML, rutas semánticas, memoria a corto/largo plazo
- **Múltiples LLM:** Ollama (local), Gemini (Google), Groq (LPU), Local (custom)
- **Sistema de Stages:** Encadenamiento de LLMs con diferentes proveedores

### RAG Avanzado (MarkItDown)
- **Parsers inteligentes:** Soporte para PDF, DOCX, XLSX, PPTX, HTML, imágenes (OCR), URLs
- **Registro de parsers:** Extensible vía decorador `@register_parser`
- **Fallback automático:** Usa parsers básicos si MarkItDown no está disponible

### UI y Experiencia de Usuario
- **Temas visuales:** YAML configurables (colores, badges, emojis)
- **Comandos CLI:** `/help`, `/exit`, `/clear`, `/agent list`, `/config show`, `/debug`
- **Historial persistente:** Comandos guardados entre sesiones
- **Autocompletado:** Tab completion para comandos slash
- **ASCII Studio:** Banners, boxes decorativos, tablas, spinners, barras de progreso

### Developer Assistant (Spec-Kit)
- **GitHub integration:** Listar repos, PRs, issues; crear PRs/issues
- **Code review:** Análisis de estilo, detección de TODOs/FIXMEs, sugerencias de documentación
- **Generación de specs:** Estructura técnica de requerimientos

### Seguridad
- **Firewall multicapa:** Ingress (regex), Egress (blacklist de comandos), Semántico (profanity)
- **Gatekeeper:** Aprobación humana con timeout (select POSIX)
- **Rate Limiting:** Ventana deslizante por usuario
- **Auditoría:** Logging de decisiones de aprobación

### Observabilidad
- **Dashboard web:** FastAPI + WebSockets (monitoreo en tiempo real)
- **Métricas Prometheus:** Endpoint `/metrics`
- **Logs JSON:** Rotación, trazabilidad con `request_id`

## 🚀 Demo con Docker (recomendada)

~~~bash
git clone https://github.com/fyjjuk/FerdoNAN
cd FerdoNAN
docker-compose -f docker-compose.demo.yml up
# En otra terminal:
docker exec -it ferdonan-ollama ollama pull phi3:mini
docker exec -it ferdonan-ollama ollama pull llama3.2:3b
# Accede al menú interactivo en la terminal donde se ejecutó docker-compose up
# Dashboard: http://localhost:8000
~~~

## 🔧 Instalación y Configuración Local

~~~bash
git clone https://github.com/fyjjuk/FerdoNAN
cd FerdoNAN
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuración (opcional)
cp .env.example .env
# Edita .env con tus API keys (Gemini, Groq, GitHub)
ollama serve  # En otra terminal
~~~

## 🎮 Uso Avanzado

### Comandos CLI
~~~bash
/help                        # Muestra ayuda
/agent list                  # Lista agentes disponibles
/agent select buscador_web   # Cambia de agente
/config show                 # Muestra configuración actual
/debug                       # Información de depuración
/clear                       # Limpia pantalla
/exit                        # Sale del asistente
~~~

### Temas Visuales
~~~bash
export FERDONAN_THEME=cyberpunk  # Tema cyberpunk
export FERDONAN_THEME=refero     # Tema por defecto
python main.py
~~~

### Localización
~~~bash
export FERDONAN_LOCALE=es  # Mensajes en español
export FERDONAN_LOCALE=en  # Inglés (por defecto)
~~~

## 🧪 Tests Unitarios (44+ tests)

~~~bash
pytest tests/ -v
# Tests específicos:
pytest tests/test_rag_unit.py -v      # RAG modular (10 tests)
pytest tests/test_interfaces.py -v    # Interfaces (7 tests)
pytest tests/test_llm_factory.py -v   # LLM factory (5 tests)
~~~

## 📚 Extensibilidad

### Crear un nuevo agente
~~~bash
mkdir -p agents/mi_agente/routes
# Crear agents/mi_agente/config.yaml
# Crear agents/mi_agente/routes/mi_ruta.yaml
~~~

### Registrar un nuevo parser de documentos
~~~python
from services.rag.parsers.registry import register_parser

@register_parser("mi_parser", extensions=[".ext"])
class MiParser:
    def parse_file(self, file_path: str) -> str:
        return text
~~~

### Crear un tema visual
~~~yaml
# ui/themes/mi_tema.yaml
name: "Mi Tema"
colors:
  primary: "#FF0000"
badges:
  agent: "[🤖]"
console:
  use_emoji: true
  use_colors: true
~~~

## 📖 Documentación Técnica

~~~bash
cd docs/build/html
python -m http.server 8000
# Abrir http://localhost:8000
~~~

Generada con Sphinx desde docstrings y archivos Markdown.

## 🤝 Contribuciones
Ver `docs/source/contributing.md`

## 📜 Licencia
MIT

## 🙏 Agradecimientos
- [Repomix](https://github.com/yamadashy/repomix) - Empaquetado de código para IA
- [ChromaDB](https://www.trychroma.com/) - Base de datos vectorial
- [Sentence Transformers](https://www.sbert.net/) - Embeddings semánticos
- [MarkItDown](https://github.com/microsoft/markitdown) - Conversión de documentos
- [PyGithub](https://pygithub.readthedocs.io/) - API de GitHub
