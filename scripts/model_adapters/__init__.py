"""Shared model adapter interfaces for security log triage."""

from scripts.model_adapters.base import AdapterResult, TriageModelAdapter
from scripts.model_adapters.openai_compatible import FineTuneAdapter, OpenAICompatibleAdapter

__all__ = [
    "AdapterResult",
    "FineTuneAdapter",
    "OpenAICompatibleAdapter",
    "TriageModelAdapter",
]
