from pydantic import BaseModel, Field
from typing import Optional, Any

class AgentManifest(BaseModel):
    id: str
    name: str
    short_term_memory_window: int = 5
    llm_provider: dict
    llm_client: Optional[Any] = None # Campo para inyección dinámica
