# Architecture Guide

## System Overview

FerdoNAN implements a **hexagonal architecture** with dependency injection.

## Core Modules

### Engine (`core/engine.py`)
Orchestrates the entire pipeline. Maintains state and dependencies.

### Pipeline (`core/pipeline.py`)
Processes user input through:
1. Sanitization
2. Ingress filtering
3. Routing
4. Gatekeeper (if required)
5. Execution (cached or fresh)
6. Egress + Semantic filtering

### Interfaces (`core/interfaces.py`)
Protocols and ABCs for dependency injection:
- `UIRendererInterface`
- `LLMClientInterface`
- `RAGEngineInterface`
- `CacheInterface`
- `GatekeeperInterface`

## Data Flow

~~~
User Input → Ingress → Sanitizer → Router → Gatekeeper → Executor → Egress → Output
~~~

## Design Principles

- **Single Responsibility**: One reason to change per class
- **Dependency Injection**: Dependencies passed explicitly
- **Open/Closed**: Extensible without modifying core
- **Package by Feature**: Related code grouped by domain
