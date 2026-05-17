"""LangChain adapters for OpenAI-compatible chat completion endpoints."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

from scripts.model_adapters.base import AdapterResult
from scripts.model_adapters.prompt_contract import (
    TRIAGE_PROMPT_VERSION,
    TRIAGE_SYSTEM_PROMPT,
    build_triage_user_prompt,
)


@dataclass(frozen=True, slots=True)
class OpenAIAdapterEnv:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: str
    max_retries: str


@dataclass(frozen=True, slots=True)
class OpenAIAdapterConfig:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: float
    max_retries: int


OPENAI_COMPATIBLE_ENV = OpenAIAdapterEnv(
    base_url="OPENAI_COMPATIBLE_BASE_URL",
    api_key="OPENAI_COMPATIBLE_API_KEY",
    model="OPENAI_COMPATIBLE_MODEL",
    timeout_seconds="OPENAI_COMPATIBLE_TIMEOUT_SECONDS",
    max_retries="OPENAI_COMPATIBLE_MAX_RETRIES",
)

OPENAI_FINETUNE_ENV = OpenAIAdapterEnv(
    base_url="OPENAI_FINETUNE_BASE_URL",
    api_key="OPENAI_FINETUNE_API_KEY",
    model="OPENAI_FINETUNE_MODEL",
    timeout_seconds="OPENAI_FINETUNE_TIMEOUT_SECONDS",
    max_retries="OPENAI_FINETUNE_MAX_RETRIES",
)


class _LangChainOpenAIAdapter:
    name: str
    env: OpenAIAdapterEnv

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        self._config, self._config_error = _build_config(
            self.env,
            base_url=base_url,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

    def analyze(self, log_line: str) -> AdapterResult:
        metadata = self._metadata()
        if self._config_error:
            return AdapterResult(
                raw_output=None,
                latency_ms=0.0,
                error=self._config_error,
                metadata=metadata,
            )

        assert self._config is not None
        start = time.perf_counter()
        try:
            response = self._invoke(log_line)
        except Exception as exc:  # pragma: no cover - endpoint errors depend on runtime config.
            return AdapterResult(
                raw_output=None,
                latency_ms=_elapsed_ms(start),
                error=f"{type(exc).__name__}: {exc}",
                metadata=metadata,
            )

        response_metadata = _extract_metadata(response)
        return AdapterResult(
            raw_output=getattr(response, "content", response),
            latency_ms=_elapsed_ms(start),
            error=None,
            metadata={
                **metadata,
                **response_metadata,
            },
        )

    def _invoke(self, log_line: str) -> Any:
        ChatOpenAI, HumanMessage, SystemMessage = _load_langchain()
        assert self._config is not None
        llm = ChatOpenAI(
            model=self._config.model,
            base_url=self._config.base_url,
            api_key=self._config.api_key,
            temperature=0,
            timeout=self._config.timeout_seconds,
            max_retries=self._config.max_retries,
        )
        return llm.invoke(
            [
                SystemMessage(content=TRIAGE_SYSTEM_PROMPT),
                HumanMessage(content=build_triage_user_prompt(log_line)),
            ]
        )

    def _metadata(self) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "adapter": self.name,
            "prompt_version": TRIAGE_PROMPT_VERSION,
            "env": {
                "base_url": self.env.base_url,
                "api_key": self.env.api_key,
                "model": self.env.model,
                "timeout_seconds": self.env.timeout_seconds,
                "max_retries": self.env.max_retries,
            },
        }
        if self._config is not None:
            metadata.update(
                {
                    "base_url": self._config.base_url,
                    "model": self._config.model,
                    "timeout_seconds": self._config.timeout_seconds,
                    "max_retries": self._config.max_retries,
                }
            )
        return metadata


class OpenAICompatibleAdapter(_LangChainOpenAIAdapter):
    """Adapter for base or generic OpenAI-compatible endpoints."""

    name = "openai-compatible"
    env = OPENAI_COMPATIBLE_ENV


class FineTuneAdapter(_LangChainOpenAIAdapter):
    """Adapter for fine-tuned models served through an OpenAI-compatible endpoint."""

    name = "openai-finetune"
    env = OPENAI_FINETUNE_ENV


def _build_config(
    env: OpenAIAdapterEnv,
    *,
    base_url: str | None,
    api_key: str | None,
    model: str | None,
    timeout_seconds: float | None,
    max_retries: int | None,
) -> tuple[OpenAIAdapterConfig | None, str | None]:
    base_url_value = base_url if base_url is not None else os.getenv(env.base_url)
    api_key_value = api_key if api_key is not None else os.getenv(env.api_key)
    model_value = model if model is not None else os.getenv(env.model)

    missing = [
        name
        for name, value in (
            (env.base_url, base_url_value),
            (env.api_key, api_key_value),
            (env.model, model_value),
        )
        if not value
    ]
    if missing:
        return None, f"Missing required environment variables: {', '.join(missing)}"

    try:
        timeout_value = _float_config(
            env.timeout_seconds,
            timeout_seconds,
            default=30.0,
            minimum=0.1,
        )
        max_retries_value = _int_config(
            env.max_retries,
            max_retries,
            default=1,
            minimum=0,
        )
    except ValueError as exc:
        return None, str(exc)

    return (
        OpenAIAdapterConfig(
            base_url=str(base_url_value),
            api_key=str(api_key_value),
            model=str(model_value),
            timeout_seconds=timeout_value,
            max_retries=max_retries_value,
        ),
        None,
    )


def _float_config(
    env_name: str,
    explicit: float | None,
    *,
    default: float,
    minimum: float,
) -> float:
    raw_value: float | str
    raw_value = explicit if explicit is not None else os.getenv(env_name, str(default))
    try:
        value = float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{env_name} must be a number") from exc
    if value < minimum:
        raise ValueError(f"{env_name} must be >= {minimum}")
    return value


def _int_config(
    env_name: str,
    explicit: int | None,
    *,
    default: int,
    minimum: int,
) -> int:
    raw_value: int | str
    raw_value = explicit if explicit is not None else os.getenv(env_name, str(default))
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{env_name} must be an integer") from exc
    if value < minimum:
        raise ValueError(f"{env_name} must be >= {minimum}")
    return value


def _load_langchain() -> tuple[Any, Any, Any]:
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Missing LangChain dependency. Install Python dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc
    return ChatOpenAI, HumanMessage, SystemMessage


def _extract_metadata(response: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    response_metadata = getattr(response, "response_metadata", None)
    usage_metadata = getattr(response, "usage_metadata", None)
    if response_metadata is not None:
        metadata["response_metadata"] = response_metadata
    if usage_metadata is not None:
        metadata["usage_metadata"] = usage_metadata
    return metadata


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 6)
