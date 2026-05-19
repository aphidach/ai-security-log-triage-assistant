"""LangChain adapters for OpenAI-compatible chat completion endpoints."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.model_adapters.base import AdapterResult
from scripts.model_adapters.prompt_contract import (
    TRIAGE_PROMPT_VERSION,
    TRIAGE_SYSTEM_PROMPT,
    build_triage_user_prompt,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = ROOT / "data" / "schemas" / "triage-output.schema.json"
PROVIDER_SCHEMA_NAME = "triage_output"

RESPONSE_FORMAT_OFF = "off"
RESPONSE_FORMAT_JSON_OBJECT = "json_object"
RESPONSE_FORMAT_JSON_SCHEMA = "json_schema"
RESPONSE_FORMAT_CHOICES = (
    RESPONSE_FORMAT_OFF,
    RESPONSE_FORMAT_JSON_OBJECT,
    RESPONSE_FORMAT_JSON_SCHEMA,
)

REQUEST_MODE_PLAIN = "plain"
REQUEST_MODE_JSON_OBJECT = "json_object"
REQUEST_MODE_JSON_SCHEMA = "json_schema_strict"
REQUEST_MODE_STRUCTURED_OUTPUTS = "structured_outputs_json"

PROVIDER_SCHEMA_ALLOWED_KEYS = frozenset(
    {
        "additionalProperties",
        "description",
        "enum",
        "items",
        "properties",
        "required",
        "type",
    }
)
FALLBACK_ERROR_PATTERNS = (
    "json schema",
    "json_schema",
    "json_object",
    "response_format",
    "structured output",
    "structured_outputs",
    "guided_json",
    "not supported",
    "unsupported",
    "invalid schema",
    "unknown field",
    "extra inputs are not permitted",
)


@dataclass(frozen=True, slots=True)
class OpenAIAdapterEnv:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: str
    max_retries: str
    response_format: str
    schema_path: str


@dataclass(frozen=True, slots=True)
class OpenAIAdapterConfig:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: float
    max_retries: int
    response_format: str
    schema_path: Path | None
    provider_schema: dict[str, Any] | None


OPENAI_COMPATIBLE_ENV = OpenAIAdapterEnv(
    base_url="OPENAI_COMPATIBLE_BASE_URL",
    api_key="OPENAI_COMPATIBLE_API_KEY",
    model="OPENAI_COMPATIBLE_MODEL",
    timeout_seconds="OPENAI_COMPATIBLE_TIMEOUT_SECONDS",
    max_retries="OPENAI_COMPATIBLE_MAX_RETRIES",
    response_format="OPENAI_COMPATIBLE_RESPONSE_FORMAT",
    schema_path="OPENAI_COMPATIBLE_SCHEMA_PATH",
)

OPENAI_FINETUNE_ENV = OpenAIAdapterEnv(
    base_url="OPENAI_FINETUNE_BASE_URL",
    api_key="OPENAI_FINETUNE_API_KEY",
    model="OPENAI_FINETUNE_MODEL",
    timeout_seconds="OPENAI_FINETUNE_TIMEOUT_SECONDS",
    max_retries="OPENAI_FINETUNE_MAX_RETRIES",
    response_format="OPENAI_FINETUNE_RESPONSE_FORMAT",
    schema_path="OPENAI_FINETUNE_SCHEMA_PATH",
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
        response_format: str | None = None,
        schema_path: str | Path | None = None,
    ) -> None:
        self._config, self._config_error = _build_config(
            self.env,
            base_url=base_url,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            response_format=response_format,
            schema_path=schema_path,
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
            response, request_mode, attempted_modes = self._invoke(log_line)
        except Exception as exc:  # pragma: no cover - endpoint errors depend on runtime config.
            return AdapterResult(
                raw_output=None,
                latency_ms=_elapsed_ms(start),
                error=f"{type(exc).__name__}: {exc}",
                metadata=metadata,
            )

        response_metadata = _extrat_metadata(response)
        print("====================\nRaw Output: ", response_metadata)
        return AdapterResult(
            raw_output=getattr(response, "content", response),
            latency_ms=_elapsed_ms(start),
            error=None,
            metadata={
                **metadata,
                "response_format_mode": request_mode,
                "response_format_attempted_modes": attempted_modes,
                **response_metadata,
            },
        )

    def _invoke(self, log_line: str) -> tuple[Any, str, list[str]]:
        ChatOpenAI, HumanMessage, SystemMessage = _load_langchain()
        assert self._config is not None
        messages = [
            SystemMessage(content=TRIAGE_SYSTEM_PROMPT),
            HumanMessage(content=build_triage_user_prompt(log_line)),
        ]
        attempted_modes: list[str] = []
        fallback_errors: list[str] = []
        for request_mode in _request_modes_for_response_format(self._config.response_format):
            attempted_modes.append(request_mode)
            llm = ChatOpenAI(
                model=self._config.model,
                base_url=self._config.base_url,
                api_key=self._config.api_key,
                temperature=0,
                timeout=self._config.timeout_seconds,
                max_retries=self._config.max_retries,
                **_request_kwargs_for_mode(request_mode, self._config.provider_schema),
            )
            try:
                return llm.invoke(messages), request_mode, attempted_modes
            except Exception as exc:  # pragma: no cover - endpoint errors depend on runtime config.
                if not _should_fallback_for_error(request_mode, exc):
                    raise
                fallback_errors.append(f"{request_mode}: {type(exc).__name__}: {exc}")

        raise RuntimeError(
            "Structured output request modes failed: " + " | ".join(fallback_errors)
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
                "response_format": self.env.response_format,
                "schema_path": self.env.schema_path,
            },
        }
        if self._config is not None:
            metadata.update(
                {
                    "base_url": self._config.base_url,
                    "model": self._config.model,
                    "timeout_seconds": self._config.timeout_seconds,
                    "max_retries": self._config.max_retries,
                    "response_format_requested": self._config.response_format,
                    "schema_path": (
                        str(self._config.schema_path.relative_to(ROOT))
                        if self._config.schema_path is not None and self._config.schema_path.is_relative_to(ROOT)
                        else (str(self._config.schema_path) if self._config.schema_path is not None else None)
                    ),
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
    response_format: str | None,
    schema_path: str | Path | None,
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
        response_format_value = _enum_config(
            env.response_format,
            response_format,
            default=RESPONSE_FORMAT_JSON_SCHEMA,
            choices=RESPONSE_FORMAT_CHOICES,
        )
    except ValueError as exc:
        return None, str(exc)

    schema_path_value: Path | None = None
    provider_schema: dict[str, Any] | None = None
    if response_format_value == RESPONSE_FORMAT_JSON_SCHEMA:
        try:
            schema_path_value = _path_config(
                env.schema_path,
                schema_path,
                default=DEFAULT_SCHEMA_PATH,
            )
            provider_schema = _sanitize_provider_schema(_load_json_schema(schema_path_value))
        except ValueError as exc:
            return None, str(exc)

    return (
        OpenAIAdapterConfig(
            base_url=str(base_url_value),
            api_key=str(api_key_value),
            model=str(model_value),
            timeout_seconds=timeout_value,
            max_retries=max_retries_value,
            response_format=response_format_value,
            schema_path=schema_path_value,
            provider_schema=provider_schema,
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


def _enum_config(
    env_name: str,
    explicit: str | None,
    *,
    default: str,
    choices: tuple[str, ...],
) -> str:
    raw_value = explicit if explicit is not None else os.getenv(env_name, default)
    value = str(raw_value).strip().lower()
    if value not in choices:
        raise ValueError(f"{env_name} must be one of: {', '.join(choices)}")
    return value


def _path_config(
    env_name: str,
    explicit: str | Path | None,
    *,
    default: Path,
) -> Path:
    raw_value = explicit if explicit is not None else os.getenv(env_name, str(default))
    candidate = Path(str(raw_value)).expanduser()
    if not candidate.is_absolute():
        candidate = (ROOT / candidate).resolve()
    if not candidate.is_file():
        raise ValueError(f"{env_name} must point to an existing file: {candidate}")
    return candidate


def _load_json_schema(path: Path) -> dict[str, Any]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"Unable to read schema file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Schema file {path} is not valid JSON: {exc}") from exc
    if not isinstance(schema, dict):
        raise ValueError(f"Schema file {path} must contain a JSON object")
    return schema


def _sanitize_provider_schema(schema: dict[str, Any]) -> dict[str, Any]:
    sanitized = _sanitize_provider_schema_node(schema)
    if not isinstance(sanitized, dict):
        raise ValueError("Provider schema must sanitize to a JSON object")
    return sanitized


def _sanitize_provider_schema_node(node: Any) -> Any:
    if isinstance(node, dict):
        sanitized: dict[str, Any] = {}
        for key, value in node.items():
            if key not in PROVIDER_SCHEMA_ALLOWED_KEYS:
                continue
            if key == "properties":
                if not isinstance(value, dict):
                    continue
                sanitized[key] = {
                    property_name: _sanitize_provider_schema_node(property_schema)
                    for property_name, property_schema in value.items()
                    if isinstance(property_name, str) and isinstance(property_schema, dict)
                }
                continue
            if key == "items":
                sanitized[key] = _sanitize_provider_schema_node(value)
                continue
            if key == "required":
                if isinstance(value, list):
                    sanitized[key] = [item for item in value if isinstance(item, str)]
                continue
            if key == "enum":
                if isinstance(value, list):
                    sanitized[key] = [item for item in value if isinstance(item, (str, int, float, bool))]
                continue
            if key == "additionalProperties":
                if isinstance(value, bool):
                    sanitized[key] = value
                elif isinstance(value, dict):
                    sanitized[key] = _sanitize_provider_schema_node(value)
                continue
            if key in {"type", "description"} and isinstance(value, str):
                sanitized[key] = value
        return sanitized
    if isinstance(node, list):
        return [_sanitize_provider_schema_node(item) for item in node]
    return node


def _request_modes_for_response_format(response_format: str) -> list[str]:
    if response_format == RESPONSE_FORMAT_OFF:
        return [REQUEST_MODE_PLAIN]
    if response_format == RESPONSE_FORMAT_JSON_OBJECT:
        return [REQUEST_MODE_JSON_OBJECT]
    return [
        REQUEST_MODE_JSON_SCHEMA,
        REQUEST_MODE_STRUCTURED_OUTPUTS,
        REQUEST_MODE_JSON_OBJECT,
    ]


def _request_kwargs_for_mode(
    request_mode: str,
    provider_schema: dict[str, Any] | None,
) -> dict[str, Any]:
    if request_mode == REQUEST_MODE_PLAIN:
        return {}
    if request_mode == REQUEST_MODE_JSON_OBJECT:
        return {"model_kwargs": {"response_format": {"type": "json_object"}}}
    if provider_schema is None:
        raise ValueError("Provider schema is required for structured output request modes")
    if request_mode == REQUEST_MODE_JSON_SCHEMA:
        return {
            "model_kwargs": {
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": PROVIDER_SCHEMA_NAME,
                        "strict": True,
                        "schema": provider_schema,
                    },
                }
            }
        }
    if request_mode == REQUEST_MODE_STRUCTURED_OUTPUTS:
        return {"extra_body": {"structured_outputs": {"json": provider_schema}}}
    raise ValueError(f"Unsupported request mode: {request_mode}")


def _should_fallback_for_error(request_mode: str, error: Exception) -> bool:
    if request_mode == REQUEST_MODE_PLAIN:
        return False
    message = str(error).lower()
    return any(pattern in message for pattern in FALLBACK_ERROR_PATTERNS)


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


def _extrat_metadata(response: Any) -> dict[str, Any]:
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
