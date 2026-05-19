#!/usr/bin/env python3
"""Probe OpenAI-compatible structured-output modes without LangChain."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Literal


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate import load_jsonl, load_schema, validate_schema  # noqa: E402
from scripts.model_adapters.openai_compatible import (  # noqa: E402
    DEFAULT_SCHEMA_PATH,
    _sanitize_provider_schema,
)
from scripts.model_adapters.prompt_contract import (  # noqa: E402
    TRIAGE_SYSTEM_PROMPT,
    build_triage_user_prompt,
)


DEFAULT_SPLIT_PATH = ROOT / "data" / "splits" / "smoke-output-contract.jsonl"
MODE_CHOICES = (
    "responses_parse",
    "json_schema",
    "structured_outputs",
    "guided_json",
    "json_object",
    "plain",
)
ENV_PREFIX_CHOICES = ("OPENAI_COMPATIBLE", "OPENAI_FINETUNE")
RESPONSES_PARSE_DEFAULT_MODEL = "current"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Send one direct chat/completions request to an OpenAI-compatible endpoint "
            "to verify whether structured output is enforced before LangChain is involved."
        )
    )
    parser.add_argument("--env-prefix", choices=ENV_PREFIX_CHOICES, default="OPENAI_COMPATIBLE")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env", help="Optional dotenv file to load first.")
    parser.add_argument("--base-url", default=None, help="Override <PREFIX>_BASE_URL.")
    parser.add_argument("--api-key", default=None, help="Override <PREFIX>_API_KEY.")
    parser.add_argument(
        "--model",
        default=None,
        help="Override <PREFIX>_MODEL. For responses_parse, default is current to match data/raw/test.py.",
    )
    parser.add_argument("--timeout-seconds", type=float, default=None, help="Override <PREFIX>_TIMEOUT_SECONDS.")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA_PATH)
    parser.add_argument("--mode", choices=MODE_CHOICES, default="json_schema")
    parser.add_argument("--split", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--sample-id", default=None, help="Use a specific JSONL record id from --split.")
    parser.add_argument("--sample-index", type=int, default=0, help="0-based record index when --sample-id is omitted.")
    parser.add_argument("--log-line", default=None, help="Use this log instead of reading --split.")
    return parser.parse_args()


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def env_value(prefix: str, suffix: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    env_name = f"{prefix}_{suffix}"
    value = os.getenv(env_name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {env_name}")
    return value


def model_value(prefix: str, mode: str, explicit: str | None = None) -> str:
    if explicit:
        return explicit
    if mode == "responses_parse":
        return RESPONSES_PARSE_DEFAULT_MODEL
    return env_value(prefix, "MODEL")


def env_float(prefix: str, suffix: str, explicit: float | None, *, default: float) -> float:
    if explicit is not None:
        return explicit
    raw_value = os.getenv(f"{prefix}_{suffix}", str(default))
    try:
        return float(raw_value)
    except ValueError as exc:
        raise SystemExit(f"{prefix}_{suffix} must be a number") from exc


def client_base_url(base_url: str) -> str:
    endpoint = base_url.rstrip("/")
    if endpoint.endswith("/chat/completions"):
        return endpoint[: -len("/chat/completions")]
    return endpoint


def endpoint_url(base_url: str) -> str:
    return f"{client_base_url(base_url).rstrip('/')}/chat/completions"


def select_log_line(args: argparse.Namespace) -> str:
    if args.log_line is not None:
        return args.log_line

    records = load_jsonl(args.split)
    if args.sample_id is not None:
        for record in records:
            if record.get("id") == args.sample_id:
                return str(record.get("input", ""))
        raise SystemExit(f"Sample id not found in {args.split}: {args.sample_id}")

    if args.sample_index < 0 or args.sample_index >= len(records):
        raise SystemExit(f"--sample-index must be between 0 and {len(records) - 1}")
    return str(records[args.sample_index].get("input", ""))


def request_kwargs(mode: str, model: str, log_line: str, provider_schema: dict[str, Any]) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
            {"role": "user", "content": build_triage_user_prompt(log_line)},
        ],
        "temperature": 0,
    }
    if mode == "json_schema":
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "triage_output",
                "strict": True,
                "schema": provider_schema,
            },
        }
    elif mode == "structured_outputs":
        kwargs["extra_body"] = {"structured_outputs": {"json": provider_schema}}
    elif mode == "guided_json":
        kwargs["extra_body"] = {"guided_json": provider_schema}
    elif mode == "json_object":
        kwargs["response_format"] = {"type": "json_object"}
    return kwargs


def triage_text_format() -> type[Any]:
    try:
        from pydantic import BaseModel
    except ImportError as exc:
        raise SystemExit("Missing Pydantic dependency. Install with `pip install pydantic`.") from exc

    class TriageProbeOutput(BaseModel):
        label: Literal[
            "normal",
            "failed_login_bruteforce",
            "sql_injection_attempt",
            "directory_traversal_attempt",
            "port_scan_or_recon",
        ]
        severity: Literal["low", "medium", "high", "critical"]
        is_suspicious: bool
        evidence: list[str]
        reason: str
        recommended_action: str

    return TriageProbeOutput


def responses_parse_kwargs(model: str, log_line: str) -> dict[str, Any]:
    return {
        "model": model,
        "input": [
            {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
            {"role": "user", "content": build_triage_user_prompt(log_line)},
        ],
        "temperature": 0,
        "text_format": triage_text_format(),
    }


def create_openai_client(base_url: str, api_key: str, timeout_seconds: float) -> Any:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise SystemExit("Missing OpenAI dependency. Install with `pip install openai`.") from exc
    return OpenAI(base_url=client_base_url(base_url), api_key=api_key, timeout=timeout_seconds)


def send_chat_completion(client: Any, kwargs: dict[str, Any]) -> Any:
    try:
        return client.chat.completions.create(**kwargs)
    except Exception as exc:
        raise SystemExit(f"OpenAI client request failed: {type(exc).__name__}: {exc}") from exc


def send_responses_parse(client: Any, kwargs: dict[str, Any]) -> Any:
    try:
        return client.responses.parse(**kwargs)
    except Exception as exc:
        raise SystemExit(f"OpenAI responses.parse request failed: {type(exc).__name__}: {exc}") from exc


def extract_content(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text:
        return output_text

    choices = getattr(response, "choices", None)
    if not choices:
        output = getattr(response, "output", None)
        if output:
            text_items: list[str] = []
            for item in output:
                for content_item in getattr(item, "content", []) or []:
                    text = getattr(content_item, "text", None)
                    if isinstance(text, str):
                        text_items.append(text)
            if text_items:
                return "\n".join(text_items)
        raise SystemExit("Endpoint response has no choices or output text")
    first_choice = choices[0]
    message = getattr(first_choice, "message", None)
    if message is None:
        raise SystemExit("Endpoint response choice has no message")
    content = getattr(message, "content", None)
    return content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)


def extract_parsed(response: Any) -> Any:
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


def main() -> int:
    args = parse_args()
    load_dotenv(args.env_file)

    base_url = env_value(args.env_prefix, "BASE_URL", args.base_url)
    api_key = env_value(args.env_prefix, "API_KEY", args.api_key)
    model = model_value(args.env_prefix, args.mode, args.model)
    timeout_seconds = env_float(args.env_prefix, "TIMEOUT_SECONDS", args.timeout_seconds, default=30.0)
    schema = load_schema(args.schema)
    provider_schema = _sanitize_provider_schema(schema)
    log_line = select_log_line(args)
    url = endpoint_url(base_url)

    client = create_openai_client(base_url, api_key, timeout_seconds)
    if args.mode == "responses_parse":
        kwargs = responses_parse_kwargs(model, log_line)
        response = send_responses_parse(client, kwargs)
    else:
        kwargs = request_kwargs(args.mode, model, log_line, provider_schema)
        response = send_chat_completion(client, kwargs)
    content = extract_content(response)

    print(f"mode: {args.mode}")
    print(f"requested_model: {model}")
    print(f"endpoint: {url}")
    response_model = getattr(response, "model", None)
    if response_model:
        print(f"response_model: {response_model}")
    parsed = extract_parsed(response)
    if parsed is not None:
        print(f"openai_parsed: {parsed}")
    print("raw_content:")
    print(content)

    try:
        parsed_output = json.loads(content)
    except json.JSONDecodeError as exc:
        print(f"json_parse_success: false ({exc})")
        return 0
    if not isinstance(parsed_output, dict):
        print(f"json_parse_success: false (parsed JSON is {type(parsed_output).__name__}, not object)")
        return 0

    schema_errors = validate_schema(parsed_output, schema)
    print("json_parse_success: true")
    print(f"schema_success: {str(not schema_errors).lower()}")
    if schema_errors:
        print("schema_errors:")
        for error in schema_errors:
            print(f"- {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
