"""Minimal single-provider (Gemini official API) client for the demo.

Stripped down from the production multi-provider client: no web-API/cookie
auth, no OpenAI-compatible provider, no context caching, no streaming batch
manager, no cost tracking. One synchronous structured-output call.

The google-genai SDK is imported lazily (inside __init__ / _generate) so the
module imports without the package and unit tests stay hermetic.
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


class GeminiClient:
    def __init__(self, api_key: str | None = None, model_name: str | None = None):
        from google import genai  # lazy: only needed for real calls
        api_key = api_key or os.environ["GEMINI_API_KEY"]
        self.model_name = model_name or os.environ.get("GEMINI_MODEL_NAME", "gemini-2.5-pro")
        self._client = genai.Client(api_key=api_key)

    def _generate(self, system_prompt: str, user_prompt: str, response_schema: dict | None = None) -> str:
        """The only SDK-touching method. Builds config and returns the response text."""
        from google.genai import types  # lazy
        kwargs = {"system_instruction": system_prompt}
        if response_schema is not None:
            kwargs["response_mime_type"] = "application/json"
            kwargs["response_schema"] = strip_additional_properties(deepcopy(response_schema))
        config = types.GenerateContentConfig(**kwargs)
        return self._client.models.generate_content(
            model=self.model_name, contents=user_prompt, config=config,
        ).text

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
