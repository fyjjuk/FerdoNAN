from pydantic import BaseModel, Field
from typing import Optional, Any, List, Literal

class RAGConfig(BaseModel):
    enabled: bool = False
    namespace: Optional[str] = None
    top_k: int = 5
    similarity_threshold: float = 0.75

class AgentManifest(BaseModel):
    id: str
    name: str
    description: str = ""
    short_term_memory_window: int = 5
    execution_mode: Literal["exclusive", "parallel"] = "exclusive"
    rag_config: RAGConfig = Field(default_factory=RAGConfig)
    llm_provider: dict = Field(default_factory=dict)
    llm_client: Optional[Any] = None
    memory: Optional[Any] = None
    firewall_override: dict = Field(default_factory=dict)
    routes_available: List[dict] = Field(default_factory=list)
    tools: dict = Field(default_factory=dict)
