"""Base protocol shared by triage model adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, runtime_checkable


@dataclass(slots=True)
class AdapterResult:
    """Raw adapter response plus metadata required by the evaluator."""

    raw_output: Any
    latency_ms: float
    error: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.error is None


@runtime_checkable
class TriageModelAdapter(Protocol):
    """Interface every triage adapter must implement."""

    name: str

    def analyze(self, log_line: str) -> AdapterResult:
        """Analyze one security log line and return raw model output."""
        ...
