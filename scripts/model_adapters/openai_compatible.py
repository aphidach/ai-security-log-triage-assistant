"""OpenAI SDK adapters for OpenAI-compatible triage endpoints."""

from __future__ import annotations

import json
import os
import ast
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, Literal

from scripts.model_adapters.base import AdapterResult
from scripts.model_adapters.prompt_contract import (
    TRIAGE_PROMPT_VERSION,
    TRIAGE_SYSTEM_PROMPT,
    build_triage_user_prompt,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = ROOT / "data" / "schemas" / "triage-output.schema.json"
DEFAULT_ADAPTER_CONFIG_PATHS = (
    ROOT / "config-adapter.yml",
    ROOT / "config-adapter.yaml",
)
PROVIDER_SCHEMA_NAME = "triage_output"
SHARED_CONFIG_PATH_ENV = "OPENAI_ADAPTER_CONFIG_PATH"

RESPONSE_FORMAT_OFF = "off"
RESPONSE_FORMAT_JSON_OBJECT = "json_object"
RESPONSE_FORMAT_JSON_SCHEMA = "json_schema"
RESPONSE_FORMAT_STRUCTURED_OUTPUTS = "structured_outputs"
RESPONSE_FORMAT_GUIDED_JSON = "guided_json"
RESPONSE_FORMAT_RESPONSES_PARSE = "responses_parse"
RESPONSE_FORMAT_CHOICES = (
    RESPONSE_FORMAT_OFF,
    RESPONSE_FORMAT_JSON_OBJECT,
    RESPONSE_FORMAT_JSON_SCHEMA,
    RESPONSE_FORMAT_STRUCTURED_OUTPUTS,
    RESPONSE_FORMAT_GUIDED_JSON,
    RESPONSE_FORMAT_RESPONSES_PARSE,
)

REQUEST_MODE_PLAIN = "plain"
REQUEST_MODE_JSON_OBJECT = "json_object"
REQUEST_MODE_JSON_SCHEMA = "json_schema_strict"
REQUEST_MODE_STRUCTURED_OUTPUTS = "structured_outputs_json"
REQUEST_MODE_GUIDED_JSON = "guided_json"
REQUEST_MODE_RESPONSES_PARSE = "responses_parse"

PROVIDER_SCHEMA_ALLOWED_KEYS = frozenset(
    {
        "additionalProperties",
        "description",
        "enum",
        "items",
        "maxItems",
        "maxLength",
        "minItems",
        "minLength",
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

CHAT_COMPLETION_REQUEST_OPTION_KEYS = frozenset(
    {
        "temperature",
        "top_p",
        "frequency_penalty",
        "presence_penalty",
        "seed",
        "stop",
    }
)
RESPONSES_PARSE_REQUEST_OPTION_KEYS = frozenset({"temperature", "top_p"})
REQUEST_OPTION_RANGES = {
    "temperature": (0.0, 2.0),
    "top_p": (0.0, 1.0),
    "frequency_penalty": (-2.0, 2.0),
    "presence_penalty": (-2.0, 2.0),
}
REQUEST_OPTION_ENV_SUFFIXES = {
    "temperature": "TEMPERATURE",
    "top_p": "TOP_P",
    "frequency_penalty": "FREQUENCY_PENALTY",
    "presence_penalty": "PRESENCE_PENALTY",
    "seed": "SEED",
    "stop": "STOP",
}
EXTRA_BODY_ENV_SUFFIX = "EXTRA_BODY"


@dataclass(frozen=True, slots=True)
class OpenAIAdapterEnv:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: str
    max_retries: str
    max_tokens: str
    response_format: str
    schema_path: str
    config_path: str


@dataclass(frozen=True, slots=True)
class OpenAIAdapterConfig:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: float
    max_retries: int
    max_tokens: int
    response_format: str
    schema_path: Path | None
    provider_schema: dict[str, Any] | None
    config_path: Path | None
    request_options: dict[str, Any]
    extra_body: dict[str, Any] | None


OPENAI_COMPATIBLE_ENV = OpenAIAdapterEnv(
    base_url="OPENAI_COMPATIBLE_BASE_URL",
    api_key="OPENAI_COMPATIBLE_API_KEY",
    model="OPENAI_COMPATIBLE_MODEL",
    timeout_seconds="OPENAI_COMPATIBLE_TIMEOUT_SECONDS",
    max_retries="OPENAI_COMPATIBLE_MAX_RETRIES",
    max_tokens="OPENAI_COMPATIBLE_MAX_TOKENS",
    response_format="OPENAI_COMPATIBLE_RESPONSE_FORMAT",
    schema_path="OPENAI_COMPATIBLE_SCHEMA_PATH",
    config_path="OPENAI_COMPATIBLE_CONFIG_PATH",
)

OPENAI_FINETUNE_ENV = OpenAIAdapterEnv(
    base_url="OPENAI_FINETUNE_BASE_URL",
    api_key="OPENAI_FINETUNE_API_KEY",
    model="OPENAI_FINETUNE_MODEL",
    timeout_seconds="OPENAI_FINETUNE_TIMEOUT_SECONDS",
    max_retries="OPENAI_FINETUNE_MAX_RETRIES",
    max_tokens="OPENAI_FINETUNE_MAX_TOKENS",
    response_format="OPENAI_FINETUNE_RESPONSE_FORMAT",
    schema_path="OPENAI_FINETUNE_SCHEMA_PATH",
    config_path="OPENAI_FINETUNE_CONFIG_PATH",
)


class _OpenAIAdapter:
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
        max_tokens: int | None = None,
        response_format: str | None = None,
        schema_path: str | Path | None = None,
        config_path: str | Path | None = None,
    ) -> None:
        self._config, self._config_error = _build_config(
            self.name,
            self.env,
            base_url=base_url,
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            max_tokens=max_tokens,
            response_format=response_format,
            schema_path=schema_path,
            config_path=config_path,
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
            raw_output, request_mode, attempted_modes, response_metadata = self._invoke(log_line)
        except Exception as exc:  # pragma: no cover - endpoint errors depend on runtime config.
            return AdapterResult(
                raw_output=None,
                latency_ms=_elapsed_ms(start),
                error=f"{type(exc).__name__}: {exc}",
                metadata=metadata,
            )

        return AdapterResult(
            raw_output=raw_output,
            latency_ms=_elapsed_ms(start),
            error=None,
            metadata={
                **metadata,
                "response_format_mode": request_mode,
                "response_format_attempted_modes": attempted_modes,
                **response_metadata,
            },
        )

    def _invoke(self, log_line: str) -> tuple[Any, str, list[str], dict[str, Any]]:
        assert self._config is not None
        client = _create_openai_client(self._config)
        if self._config.response_format == RESPONSE_FORMAT_RESPONSES_PARSE:
            response = client.responses.parse(
                model=self._config.model,
                input=_message_payload(log_line),
                max_output_tokens=self._config.max_tokens,
                text_format=_triage_output_model(),
                **_responses_parse_request_options(self._config.request_options),
            )
            parsed = _extract_responses_parsed(response)
            if parsed is None:
                raise RuntimeError("OpenAI responses.parse returned no parsed output")
            return (
                _parsed_output_to_dict(parsed),
                REQUEST_MODE_RESPONSES_PARSE,
                [REQUEST_MODE_RESPONSES_PARSE],
                _extract_metadata(response),
            )

        attempted_modes: list[str] = []
        fallback_errors: list[str] = []
        for request_mode in _request_modes_for_response_format(self._config.response_format):
            attempted_modes.append(request_mode)
            request_kwargs = _chat_completion_kwargs(
                request_mode=request_mode,
                model=self._config.model,
                log_line=log_line,
                max_tokens=self._config.max_tokens,
                provider_schema=self._config.provider_schema,
                request_options=self._config.request_options,
                extra_body=self._config.extra_body,
            )
            try:
                response = client.chat.completions.create(**request_kwargs)
                return (
                    _extract_chat_content(response),
                    request_mode,
                    attempted_modes,
                    _extract_metadata(response),
                )
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
                "max_tokens": self.env.max_tokens,
                "response_format": self.env.response_format,
                "schema_path": self.env.schema_path,
                "config_path": self.env.config_path,
                "shared_config_path": SHARED_CONFIG_PATH_ENV,
                "temperature": _request_option_env_name(self.env, "temperature"),
                "top_p": _request_option_env_name(self.env, "top_p"),
                "frequency_penalty": _request_option_env_name(self.env, "frequency_penalty"),
                "presence_penalty": _request_option_env_name(self.env, "presence_penalty"),
                "seed": _request_option_env_name(self.env, "seed"),
                "stop": _request_option_env_name(self.env, "stop"),
                "extra_body": _extra_body_env_name(self.env),
            },
        }
        if self._config is not None:
            metadata.update(
                {
                    "base_url": self._config.base_url,
                    "model": self._config.model,
                    "requested_model": self._config.model,
                    "timeout_seconds": self._config.timeout_seconds,
                    "max_retries": self._config.max_retries,
                    "max_tokens": self._config.max_tokens,
                    "response_format_requested": self._config.response_format,
                    "config_path": (
                        str(self._config.config_path.relative_to(ROOT))
                        if self._config.config_path is not None and self._config.config_path.is_relative_to(ROOT)
                        else (str(self._config.config_path) if self._config.config_path is not None else None)
                    ),
                    "request_options": self._config.request_options,
                    "extra_body": self._config.extra_body,
                    "schema_path": (
                        str(self._config.schema_path.relative_to(ROOT))
                        if self._config.schema_path is not None and self._config.schema_path.is_relative_to(ROOT)
                        else (str(self._config.schema_path) if self._config.schema_path is not None else None)
                    ),
                }
            )
        return metadata


class OpenAICompatibleAdapter(_OpenAIAdapter):
    """Adapter for base or generic OpenAI-compatible endpoints."""

    name = "openai-compatible"
    env = OPENAI_COMPATIBLE_ENV


class FineTuneAdapter(_OpenAIAdapter):
    """Adapter for fine-tuned models served through an OpenAI-compatible endpoint."""

    name = "openai-finetune"
    env = OPENAI_FINETUNE_ENV


def _build_config(
    adapter_name: str,
    env: OpenAIAdapterEnv,
    *,
    base_url: str | None,
    api_key: str | None,
    model: str | None,
    timeout_seconds: float | None,
    max_retries: int | None,
    max_tokens: int | None,
    response_format: str | None,
    schema_path: str | Path | None,
    config_path: str | Path | None,
) -> tuple[OpenAIAdapterConfig | None, str | None]:
    try:
        config_path_value = _adapter_config_path(env, config_path)
        file_config = _adapter_file_config(config_path_value, adapter_name)
        response_format_value = _enum_config(
            env.response_format,
            response_format,
            config_value=file_config.get("response_format"),
            default=RESPONSE_FORMAT_RESPONSES_PARSE,
            choices=RESPONSE_FORMAT_CHOICES,
        )
        timeout_value = _float_config(
            env.timeout_seconds,
            timeout_seconds,
            config_value=file_config.get("timeout_seconds"),
            default=30.0,
            minimum=0.1,
        )
        max_retries_value = _int_config(
            env.max_retries,
            max_retries,
            config_value=file_config.get("max_retries"),
            default=1,
            minimum=0,
        )
        max_tokens_value = _int_config(
            env.max_tokens,
            max_tokens,
            config_value=file_config.get("max_tokens"),
            default=512,
            minimum=1,
        )
        request_options, extra_body = _request_config(file_config, env=env)
    except ValueError as exc:
        return None, str(exc)

    base_url_value = _string_config(env.base_url, base_url, config_value=file_config.get("base_url"))
    api_key_value = _string_config(env.api_key, api_key, config_value=file_config.get("api_key"))
    model_value = _string_config(env.model, model, config_value=file_config.get("model"))
    if not model_value and response_format_value == RESPONSE_FORMAT_RESPONSES_PARSE:
        model_value = "current"

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

    schema_path_value: Path | None = None
    provider_schema: dict[str, Any] | None = None
    if response_format_value in {
        RESPONSE_FORMAT_JSON_SCHEMA,
        RESPONSE_FORMAT_STRUCTURED_OUTPUTS,
        RESPONSE_FORMAT_GUIDED_JSON,
    }:
        try:
            schema_path_value = _path_config(
                env.schema_path,
                schema_path,
                config_value=file_config.get("schema_path"),
                default=DEFAULT_SCHEMA_PATH,
            )
            provider_schema = _sanitize_provider_schema(_load_json_schema(schema_path_value))
        except ValueError as exc:
            return None, str(exc)

    return (
        OpenAIAdapterConfig(
            base_url=_client_base_url(str(base_url_value)),
            api_key=str(api_key_value),
            model=str(model_value),
            timeout_seconds=timeout_value,
            max_retries=max_retries_value,
            max_tokens=max_tokens_value,
            response_format=response_format_value,
            schema_path=schema_path_value,
            provider_schema=provider_schema,
            config_path=config_path_value,
            request_options=request_options,
            extra_body=extra_body,
        ),
        None,
    )


def _adapter_config_path(env: OpenAIAdapterEnv, explicit: str | Path | None) -> Path | None:
    raw_value = explicit or os.getenv(env.config_path) or os.getenv(SHARED_CONFIG_PATH_ENV)
    if raw_value:
        candidate = _resolve_repo_path(raw_value)
        if not candidate.is_file():
            raise ValueError(f"{env.config_path} must point to an existing file: {candidate}")
        return candidate

    for candidate in DEFAULT_ADAPTER_CONFIG_PATHS:
        if candidate.is_file():
            return candidate.resolve()
    return None


def _adapter_file_config(path: Path | None, adapter_name: str) -> dict[str, Any]:
    if path is None:
        return {}
    config = _load_yaml_object(path)
    defaults = _mapping_config(config.get("defaults"), field_name=f"{path}:defaults")
    adapter_section = (
        config.get(adapter_name)
        or config.get(adapter_name.replace("-", "_"))
        or config.get(adapter_name.replace("-", ""))
    )
    adapter_config = _mapping_config(adapter_section, field_name=f"{path}:{adapter_name}")
    return _deep_merge(defaults, adapter_config)


def _string_config(env_name: str, explicit: str | None, *, config_value: Any = None) -> str | None:
    if explicit is not None:
        return explicit
    env_value = os.getenv(env_name)
    if env_value is not None:
        return env_value
    if config_value is None:
        return None
    if not isinstance(config_value, (str, int, float)):
        raise ValueError(f"{env_name} must be a string")
    return str(config_value)


def _float_config(
    env_name: str,
    explicit: float | None,
    *,
    config_value: Any = None,
    default: float,
    minimum: float,
) -> float:
    raw_value: float | str
    env_value = os.getenv(env_name)
    raw_value = (
        explicit
        if explicit is not None
        else env_value
        if env_value is not None
        else config_value
        if config_value is not None
        else str(default)
    )
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
    config_value: Any = None,
    default: int,
    minimum: int,
) -> int:
    raw_value: int | str
    env_value = os.getenv(env_name)
    raw_value = (
        explicit
        if explicit is not None
        else env_value
        if env_value is not None
        else config_value
        if config_value is not None
        else str(default)
    )
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
    config_value: Any = None,
    default: str,
    choices: tuple[str, ...],
) -> str:
    env_value = os.getenv(env_name)
    raw_value = (
        explicit
        if explicit is not None
        else env_value
        if env_value is not None
        else config_value
        if config_value is not None
        else default
    )
    value = str(raw_value).strip().lower()
    if value not in choices:
        raise ValueError(f"{env_name} must be one of: {', '.join(choices)}")
    return value


def _path_config(
    env_name: str,
    explicit: str | Path | None,
    *,
    config_value: Any = None,
    default: Path,
) -> Path:
    env_value = os.getenv(env_name)
    raw_value = (
        explicit
        if explicit is not None
        else env_value
        if env_value is not None
        else config_value
        if config_value is not None
        else str(default)
    )
    candidate = _resolve_repo_path(raw_value)
    if not candidate.is_file():
        raise ValueError(f"{env_name} must point to an existing file: {candidate}")
    return candidate


def _resolve_repo_path(value: str | Path) -> Path:
    candidate = Path(str(value)).expanduser()
    if not candidate.is_absolute():
        candidate = (ROOT / candidate).resolve()
    return candidate.resolve()


def _request_config(
    config: dict[str, Any],
    *,
    env: OpenAIAdapterEnv | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    request = _mapping_config(config.get("request"), field_name="request")
    request_options: dict[str, Any] = {"temperature": 0}
    extra_body = request.get("extra_body")
    if extra_body is not None and not isinstance(extra_body, dict):
        raise ValueError("request.extra_body must be a YAML object")

    for key, value in request.items():
        if key == "extra_body":
            continue
        if key not in CHAT_COMPLETION_REQUEST_OPTION_KEYS:
            allowed = ", ".join(sorted(CHAT_COMPLETION_REQUEST_OPTION_KEYS | {"extra_body"}))
            raise ValueError(f"request.{key} is not supported. Allowed keys: {allowed}")
        if value is None:
            continue
        request_options[key] = _validate_request_option(key, value)

    if env is not None:
        for key in sorted(REQUEST_OPTION_ENV_SUFFIXES):
            env_name = _request_option_env_name(env, key)
            env_value = os.getenv(env_name)
            if env_value is None:
                continue
            request_options[key] = _validate_request_option(
                key,
                _parse_request_option_env_value(key, env_value, env_name=env_name),
            )

        extra_body_env = _extra_body_env_name(env)
        extra_body_value = os.getenv(extra_body_env)
        if extra_body_value is not None:
            parsed_extra_body = _parse_extra_body_env_value(extra_body_value, env_name=extra_body_env)
            extra_body = parsed_extra_body

    return request_options, dict(extra_body) if isinstance(extra_body, dict) and extra_body else None


def _adapter_env_prefix(env: OpenAIAdapterEnv) -> str:
    return env.model.removesuffix("_MODEL")


def _request_option_env_name(env: OpenAIAdapterEnv, key: str) -> str:
    return f"{_adapter_env_prefix(env)}_{REQUEST_OPTION_ENV_SUFFIXES[key]}"


def _extra_body_env_name(env: OpenAIAdapterEnv) -> str:
    return f"{_adapter_env_prefix(env)}_{EXTRA_BODY_ENV_SUFFIX}"


def _parse_request_option_env_value(key: str, value: str, *, env_name: str) -> Any:
    if key in REQUEST_OPTION_RANGES:
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"{env_name} must be a number") from exc
    if key == "seed":
        try:
            return int(value)
        except ValueError as exc:
            raise ValueError(f"{env_name} must be an integer") from exc
    if key == "stop":
        stripped = value.strip()
        if stripped.startswith("["):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{env_name} must be a string or JSON string array") from exc
        return value
    return value


def _parse_extra_body_env_value(value: str, *, env_name: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{env_name} must be a JSON object") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{env_name} must be a JSON object")
    return parsed


def _validate_request_option(key: str, value: Any) -> Any:
    if key in REQUEST_OPTION_RANGES:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"request.{key} must be a number")
        minimum, maximum = REQUEST_OPTION_RANGES[key]
        numeric_value = float(value)
        if not minimum <= numeric_value <= maximum:
            raise ValueError(f"request.{key} must be between {minimum} and {maximum}")
        return numeric_value
    if key == "seed":
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("request.seed must be an integer")
        return value
    if key == "stop":
        if isinstance(value, str):
            return value
        if isinstance(value, list) and all(isinstance(item, str) and item for item in value):
            return value
        raise ValueError("request.stop must be a string or list of strings")
    raise ValueError(f"Unsupported request option: {key}")


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


def _load_yaml_object(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        config = _load_simple_yaml_object(path)
    else:
        try:
            config = yaml.safe_load(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise ValueError(f"Unable to read adapter config file {path}: {exc}") from exc

    if config is None:
        return {}
    if not isinstance(config, dict):
        raise ValueError(f"Adapter config file {path} must contain a YAML object")
    return config


def _load_simple_yaml_object(path: Path) -> dict[str, Any]:
    try:
        raw_lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"Unable to read adapter config file {path}: {exc}") from exc

    parsed_lines: list[tuple[int, int, str]] = []
    for line_number, raw_line in enumerate(raw_lines, start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line[: len(raw_line) - len(raw_line.lstrip())]:
            raise ValueError(f"{path}:{line_number}: indentation must use spaces")
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        parsed_lines.append((line_number, indent, raw_line.strip()))

    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    for index, (line_number, indent, line) in enumerate(parsed_lines):
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ValueError(f"{path}:{line_number}: invalid indentation")
        parent = stack[-1][1]

        if line.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError(f"{path}:{line_number}: list item appears outside a list")
            parent.append(_parse_yaml_scalar(line[2:].strip()))
            continue

        if ":" not in line:
            raise ValueError(f"{path}:{line_number}: expected `key: value`")
        if not isinstance(parent, dict):
            raise ValueError(f"{path}:{line_number}: mapping entry appears inside a scalar list")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"{path}:{line_number}: empty key")
        raw_value = raw_value.strip()
        if raw_value:
            parent[key] = _parse_yaml_scalar(raw_value)
            continue

        next_line = next((candidate for candidate in parsed_lines[index + 1 :] if candidate[1] > indent), None)
        container: dict[str, Any] | list[Any]
        container = [] if next_line is not None and next_line[2].startswith("- ") else {}
        parent[key] = container
        stack.append((indent, container))

    return root


def _parse_yaml_scalar(value: str) -> Any:
    normalized = value.strip().lower()
    if normalized in {"null", "none", "~"}:
        return None
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    if value.startswith(("'", '"')):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value.strip("'\"")
    if value.startswith("[") or value.startswith("{"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def _mapping_config(value: Any, *, field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a YAML object")
    return dict(value)


def _deep_merge(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    merged = dict(left)
    for key, value in right.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


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
                continue
            if key in {"minItems", "maxItems", "minLength", "maxLength"}:
                if isinstance(value, int) and not isinstance(value, bool):
                    sanitized[key] = value
                continue
        return sanitized
    if isinstance(node, list):
        return [_sanitize_provider_schema_node(item) for item in node]
    return node


def _client_base_url(base_url: str) -> str:
    endpoint = base_url.rstrip("/")
    if endpoint.endswith("/chat/completions"):
        return endpoint[: -len("/chat/completions")]
    return endpoint


def _message_payload(log_line: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
        {"role": "user", "content": build_triage_user_prompt(log_line)},
    ]


def _request_modes_for_response_format(response_format: str) -> list[str]:
    if response_format == RESPONSE_FORMAT_OFF:
        return [REQUEST_MODE_PLAIN]
    if response_format == RESPONSE_FORMAT_JSON_OBJECT:
        return [REQUEST_MODE_JSON_OBJECT]
    if response_format == RESPONSE_FORMAT_STRUCTURED_OUTPUTS:
        return [REQUEST_MODE_STRUCTURED_OUTPUTS]
    if response_format == RESPONSE_FORMAT_GUIDED_JSON:
        return [REQUEST_MODE_GUIDED_JSON]
    if response_format == RESPONSE_FORMAT_RESPONSES_PARSE:
        return [REQUEST_MODE_RESPONSES_PARSE]
    return [
        REQUEST_MODE_JSON_SCHEMA,
        REQUEST_MODE_STRUCTURED_OUTPUTS,
        REQUEST_MODE_JSON_OBJECT,
    ]


def _chat_completion_kwargs(
    *,
    request_mode: str,
    model: str,
    log_line: str,
    max_tokens: int,
    provider_schema: dict[str, Any] | None,
    request_options: dict[str, Any],
    extra_body: dict[str, Any] | None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": _message_payload(log_line),
        "max_tokens": max_tokens,
        **request_options,
    }
    if request_mode == REQUEST_MODE_PLAIN:
        _apply_extra_body(kwargs, extra_body)
        return kwargs
    if request_mode == REQUEST_MODE_JSON_OBJECT:
        kwargs["response_format"] = {"type": "json_object"}
        _apply_extra_body(kwargs, extra_body)
        return kwargs
    if provider_schema is None:
        raise ValueError("Provider schema is required for structured output request modes")
    if request_mode == REQUEST_MODE_JSON_SCHEMA:
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": PROVIDER_SCHEMA_NAME,
                "strict": True,
                "schema": provider_schema,
            },
        }
        _apply_extra_body(kwargs, extra_body)
        return kwargs
    if request_mode == REQUEST_MODE_STRUCTURED_OUTPUTS:
        _apply_extra_body(kwargs, extra_body, {"structured_outputs": {"json": provider_schema}})
        return kwargs
    if request_mode == REQUEST_MODE_GUIDED_JSON:
        _apply_extra_body(kwargs, extra_body, {"guided_json": provider_schema})
        return kwargs
    raise ValueError(f"Unsupported request mode: {request_mode}")


def _responses_parse_request_options(request_options: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in request_options.items()
        if key in RESPONSES_PARSE_REQUEST_OPTION_KEYS
    }


def _apply_extra_body(
    kwargs: dict[str, Any],
    configured_extra_body: dict[str, Any] | None,
    mode_extra_body: dict[str, Any] | None = None,
) -> None:
    merged_extra_body = _deep_merge(configured_extra_body or {}, mode_extra_body or {})
    if merged_extra_body:
        kwargs["extra_body"] = merged_extra_body


def _should_fallback_for_error(request_mode: str, error: Exception) -> bool:
    if request_mode == REQUEST_MODE_PLAIN:
        return False
    message = str(error).lower()
    return any(pattern in message for pattern in FALLBACK_ERROR_PATTERNS)


def _create_openai_client(config: OpenAIAdapterConfig) -> Any:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Missing OpenAI dependency. Install Python dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc
    return OpenAI(
        base_url=config.base_url,
        api_key=config.api_key,
        timeout=config.timeout_seconds,
        max_retries=config.max_retries,
    )


def _triage_output_model() -> type[Any]:
    try:
        from pydantic import BaseModel, ConfigDict, Field, field_validator
    except ImportError as exc:
        raise RuntimeError(
            "Missing Pydantic dependency. Install Python dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc

    class TriageOutput(BaseModel):
        model_config = ConfigDict(extra="forbid")

        label: Literal[
            "normal",
            "failed_login_bruteforce",
            "sql_injection_attempt",
            "directory_traversal_attempt",
            "port_scan_or_recon",
        ]
        severity: Literal["low", "medium", "high", "critical"]
        is_suspicious: bool
        evidence: Annotated[
            list[Annotated[str, Field(min_length=1, max_length=160)]],
            Field(min_length=1, max_length=3),
        ]
        reason: str
        recommended_action: str

        @field_validator("evidence")
        @classmethod
        def evidence_items_must_be_non_empty(cls, value: list[str]) -> list[str]:
            if not 1 <= len(value) <= 3:
                raise ValueError("evidence must contain one to three items")
            if any(not isinstance(item, str) or not item or len(item) > 160 for item in value):
                raise ValueError("evidence items must be non-empty strings up to 160 characters")
            return value

        @field_validator("reason", "recommended_action")
        @classmethod
        def text_fields_must_be_non_empty(cls, value: str) -> str:
            if not isinstance(value, str) or not value:
                raise ValueError("field must be a non-empty string")
            return value

    return TriageOutput


def _extract_responses_parsed(response: Any) -> Any:
    output_parsed = getattr(response, "output_parsed", None)
    if output_parsed is not None:
        return output_parsed

    output = getattr(response, "output", None)
    if output:
        for item in output:
            for content_item in getattr(item, "content", []) or []:
                parsed = getattr(content_item, "parsed", None)
                if parsed is not None:
                    return parsed
    return None


def _parsed_output_to_dict(parsed: Any) -> dict[str, Any]:
    if isinstance(parsed, dict):
        return parsed
    model_dump = getattr(parsed, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump()
        if isinstance(dumped, dict):
            return dumped
    raise RuntimeError(f"Parsed output is {type(parsed).__name__}, not a dict-like Pydantic model")


def _extract_chat_content(response: Any) -> str:
    choices = getattr(response, "choices", None)
    if not choices:
        raise RuntimeError("OpenAI chat completion response has no choices")
    first_choice = choices[0]
    message = getattr(first_choice, "message", None)
    if message is None:
        raise RuntimeError("OpenAI chat completion response choice has no message")
    content = getattr(message, "content", None)
    return content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)


def _extract_metadata(response: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    response_model = getattr(response, "model", None)
    if response_model is not None:
        metadata["response_model"] = response_model
    response_id = getattr(response, "id", None)
    if response_id is not None:
        metadata["response_id"] = response_id
    finish_reason = _extract_finish_reason(response)
    if finish_reason is not None:
        metadata["finish_reason"] = finish_reason
    usage = getattr(response, "usage", None)
    if usage is not None:
        metadata["usage"] = _metadata_value(usage)
    return metadata


def _extract_finish_reason(response: Any) -> str | None:
    choices = getattr(response, "choices", None)
    if choices:
        return getattr(choices[0], "finish_reason", None)
    status = getattr(response, "status", None)
    return status if isinstance(status, str) else None


def _metadata_value(value: Any) -> Any:
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return model_dump()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_metadata_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _metadata_value(item) for key, item in value.items()}
    return repr(value)


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 6)
