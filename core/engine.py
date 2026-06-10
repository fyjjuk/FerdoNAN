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

    def set_rag_engine(self, rag_engine):
        self.rag_engine = rag_engine

    def process_pipeline(self, agent_manifest, raw_input: str) -> Tuple[str, Dict[str, Any]]:
        return run_pipeline(
            agent_manifest=agent_manifest,
            raw_input=raw_input,
            ingress=self.ingress,
            egress=self.egress,
            semantic=self.semantic,
            gatekeeper=self.gatekeeper,
            cache=self.cache,
            rag_engine=self.rag_engine,
            core_config=self.core_config
        )
