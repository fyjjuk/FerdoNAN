from pydantic import BaseModel, Field
from typing import Optional, Any, List, Literal, Dict

class RAGConfig(BaseModel):
    enabled: bool = False
    namespace: Optional[str] = None
    top_k: int = 5
    similarity_threshold: float = 0.75

class RouterConfig(BaseModel):
    mode: Literal["keyword", "ollama", "embedding", "hybrid"] = "keyword"
    model: Optional[str] = None  # ej. "tinyllama" para modo ollama
    threshold: float = 0.3

class SanitizerConfig(BaseModel):
    enabled: bool = True
    use_llm: bool = False   # si True, usar modelo pequeño (requiere model)
    model: Optional[str] = None

class AgentManifest(BaseModel):
    id: str
    name: str
    description: str = ""
    short_term_memory_window: int = 5
    execution_mode: Literal["exclusive", "parallel"] = "exclusive"
    execution_timeout: int = 30  # Timeout por defecto para ejecuciones de este agente
    rag_config: RAGConfig = Field(default_factory=RAGConfig)
    router_config: RouterConfig = Field(default_factory=RouterConfig)
    sanitizer_config: SanitizerConfig = Field(default_factory=SanitizerConfig)
    llm_provider: dict = Field(default_factory=dict)
    llm_client: Optional[Any] = None
    memory: Optional[Any] = None
    long_term_memory: Optional[Any] = None
    firewall_override: dict = Field(default_factory=dict)
    routes_available: List[dict] = Field(default_factory=list)
    tools: dict = Field(default_factory=dict)
