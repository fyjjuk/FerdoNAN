from typing import Tuple, Dict, Any
from orchestration.resource_manager import ResourceScheduler
from security.filters.ingress import IngressFilter
from security.filters.egress import EgressFilter
from security.filters.semantic import SemanticOutputFilter
from persistence.cache import ResponseCache
from core.pipeline import run_pipeline

class FerdoNANEngine:
    def __init__(self, ingress: IngressFilter, egress: EgressFilter, semantic: SemanticOutputFilter,
                 gatekeeper=None, cache=None, rag_engine=None):
        self.ingress = ingress
        self.egress = egress
        self.semantic = semantic
        self.scheduler = ResourceScheduler()
        self.cache = cache if cache is not None else ResponseCache()
        self.gatekeeper = gatekeeper
        self.core_config = {}
        self.rag_engine = rag_engine
        self.ui = ui_renderer

    def set_rag_engine(self, rag_engine):
        self.rag_engine = rag_engine
        self.ui = ui_renderer

    def process_pipeline(self, agent_manifest, raw_input: str, core_config: dict = None) -> Tuple[str, Dict[str, Any]]:
        # Usar core_config pasado como parámetro o el del engine
        if core_config is None:
            core_config = self.core_config
        return run_pipeline(
            agent_manifest=agent_manifest,
            raw_input=raw_input,
            ingress=self.ingress,
            egress=self.egress,
            semantic=self.semantic,
            gatekeeper=self.gatekeeper,
            cache=self.cache,
            rag_engine=self.rag_engine,
            core_config=core_config
        )

    # Control de concurrencia
    _semaphore = None
    
    @classmethod
    def get_semaphore(cls, max_concurrent: int = 5):
        """Obtiene o crea un semáforo para limitar concurrencia."""
        if cls._semaphore is None:
            import threading
            cls._semaphore = threading.Semaphore(max_concurrent)
        return cls._semaphore
    
    def execute_with_limit(self, func, *args, **kwargs):
        """Ejecuta una función con límite de concurrencia."""
        semaphore = self.get_semaphore()
        with semaphore:
            return func(*args, **kwargs)
