"""Minimal LLM clients for the demo, supporting two providers.

Stripped down from the production multi-provider client: no web-API/cookie
auth, no context caching, no streaming batch manager, no cost tracking. One
synchronous call per request.

Providers (selected by the LLM_PROVIDER env var, default "openai"):
  * "openai"  -> OpenAICompatibleClient (OpenRouter / OpenAI / Azure, etc.)
  * "gemini"  -> GeminiClient (Google AI official API, optional custom gateway)

SDKs (google-genai / openai) are imported lazily so the module imports without
either package installed and unit tests stay hermetic (they bypass __init__
and replace `_generate`).
"""
import json
import os
from copy import deepcopy


def strip_additional_properties(schema):
    """Recursively remove `additionalProperties` keys.

    Gemini's structured-output JSON-Schema dialect rejects this keyword.
    """
    if isinstance(schema, dict):
        return {k: strip_additional_properties(v)
                for k, v in schema.items() if k != "additionalProperties"}
    if isinstance(schema, list):
        return [strip_additional_properties(v) for v in schema]
    return schema


class _BaseClient:
    """Shared parse/retry logic. Subclasses implement `_generate`."""

    def complete_json(self, system_prompt: str, user_prompt: str, response_schema: dict) -> dict:
        """Structured-output call returning parsed JSON. Retries once on parse failure."""
        last_err = None
        for _ in range(2):
            raw = self._generate(system_prompt, user_prompt, response_schema)
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, TypeError) as e:
                last_err = e
        raise ValueError(f"Failed to parse JSON after retry: {last_err}")

    def complete_text(self, system_prompt: str, user_prompt: str) -> str:
        """Plain-text call (used by de-identification, which returns tagged text)."""
        return self._generate(system_prompt, user_prompt)

    def _generate(self, system_prompt: str, user_prompt: str, response_schema: dict | None = None) -> str:
        raise NotImplementedError


class GeminiClient(_BaseClient):
    """Google AI official API (google-genai). Optional custom gateway via GEMINI_API_ENDPOINT."""

    def __init__(self, api_key: str | None = None, model_name: str | None = None,
                 api_endpoint: str | None = None):
        from google import genai  # lazy
        api_key = api_key or os.environ["GEMINI_API_KEY"]
        self.model_name = model_name or os.environ.get("GEMINI_MODEL_NAME", "gemini-3.1-pro-preview")
        api_endpoint = api_endpoint or os.environ.get("GEMINI_API_ENDPOINT")
        client_kwargs = {"api_key": api_key}
        if api_endpoint:
            client_kwargs["http_options"] = {"base_url": api_endpoint}
        self._client = genai.Client(**client_kwargs)

    def _generate(self, system_prompt: str, user_prompt: str, response_schema: dict | None = None) -> str:
        from google.genai import types  # lazy
        kwargs = {"system_instruction": system_prompt}
        if response_schema is not None:
            kwargs["response_mime_type"] = "application/json"
            kwargs["response_schema"] = strip_additional_properties(deepcopy(response_schema))
        config = types.GenerateContentConfig(**kwargs)
        return self._client.models.generate_content(
            model=self.model_name, contents=user_prompt, config=config,
        ).text


class OpenAICompatibleClient(_BaseClient):
    """OpenAI-compatible Chat Completions (OpenRouter by default; also OpenAI/Azure).

    JSON is requested via response_format={"type": "json_object"} and validated
    downstream by the caller's pydantic model — robust across providers without
    depending on provider-specific strict json_schema support.
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None,
                 model_name: str | None = None, reasoning_effort: str | None = None):
        from openai import OpenAI  # lazy
        api_key = api_key or os.environ["OPENAI_API_KEY"]
        base_url = base_url or os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        self.model_name = model_name or os.environ.get("OPENAI_MODEL_NAME", "google/gemini-3.1-pro-preview")
        self.reasoning_effort = reasoning_effort or os.environ.get("OPENAI_REASONING_EFFORT")
        self._client = OpenAI(base_url=base_url, api_key=api_key)

    def _build_messages(self, system_prompt: str, user_prompt: str,
                        response_schema: dict | None = None) -> list[dict]:
        """Assemble chat messages, conveying the output schema to the model.

        json_object mode only guarantees *valid* JSON, not the right *fields*.
        Gemini's native response_schema enforces the field contract; some prompts
        (e.g. patient_verification) rely on that and do not restate their fields.
        To reproduce that enforcement portably, we append the JSON Schema to the
        user turn so the model emits exactly the expected field names.
        """
        user_content = user_prompt
        if response_schema is not None:
            user_content += (
                "\n\n---\nReturn ONLY valid JSON, no markdown fences. Each result "
                "object MUST use exactly the field names defined by this JSON "
                "Schema (no extra or renamed keys):\n"
                + json.dumps(response_schema, ensure_ascii=False))
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

    def _generate(self, system_prompt: str, user_prompt: str, response_schema: dict | None = None) -> str:
        kwargs = {
            "model": self.model_name,
            "messages": self._build_messages(system_prompt, user_prompt, response_schema),
        }
        if response_schema is not None:
            kwargs["response_format"] = {"type": "json_object"}
        if self.reasoning_effort:
            kwargs["reasoning_effort"] = self.reasoning_effort
        return self._client.chat.completions.create(**kwargs).choices[0].message.content


def unwrap_one(result):
    """Normalize a batch-style response to a single object.

    The prompts are batch-oriented: they may return a JSON array of per-item
    results, or an ``{"items": [...]}`` envelope (strict structured-output
    providers wrap top-level arrays). The demo sends one item and expects one
    object, so unwrap to the first element. A plain object passes through.
    """
    if isinstance(result, dict) and isinstance(result.get("items"), list):
        result = result["items"]
    if isinstance(result, list):
        if not result:
            raise ValueError("model returned an empty result list")
        return result[0]
    return result


def select_client_class(provider: str):
    """Map a provider name to its client class."""
    p = (provider or "").lower()
    if p in ("openai", "openrouter"):
        return OpenAICompatibleClient
    if p in ("gemini", "google", "official"):
        return GeminiClient
    raise ValueError(f"Unknown LLM_PROVIDER '{provider}' (use 'openai' or 'gemini')")


def make_client(provider: str | None = None) -> _BaseClient:
    """Construct the client for the configured provider (env LLM_PROVIDER, default 'openai')."""
    provider = provider or os.environ.get("LLM_PROVIDER", "openai")
    return select_client_class(provider)()
