import json
import pytest
from src.llm_client import (
    strip_additional_properties, GeminiClient, OpenAICompatibleClient,
    select_client_class, unwrap_one,
)

def test_unwrap_one_handles_object_list_and_items_envelope():
    assert unwrap_one({"state": "STABLE"}) == {"state": "STABLE"}      # plain object
    assert unwrap_one([{"a": 1}, {"a": 2}]) == {"a": 1}                # bare array -> first
    assert unwrap_one({"items": [{"b": 3}]}) == {"b": 3}              # envelope -> first
    with pytest.raises(ValueError):
        unwrap_one([])

def test_strip_additional_properties_recursive():
    schema = {"type": "object", "additionalProperties": False,
              "properties": {"a": {"type": "object", "additionalProperties": False,
                                   "properties": {"b": {"type": "string"}}}}}
    cleaned = strip_additional_properties(schema)
    assert "additionalProperties" not in cleaned
    assert "additionalProperties" not in cleaned["properties"]["a"]

def _client_with(cls, outputs):
    c = cls.__new__(cls)                        # bypass __init__ (no SDK / no API key)
    c.model_name = "fake"
    seq = list(outputs); calls = {"n": 0}
    def fake_generate(system_prompt, user_prompt, response_schema=None):
        i = calls["n"]; calls["n"] += 1; return seq[i]
    c._generate = fake_generate
    c._calls = calls
    return c

@pytest.mark.parametrize("cls", [GeminiClient, OpenAICompatibleClient])
def test_complete_json_parses_valid(cls):
    c = _client_with(cls, ['{"x": 1}'])
    assert c.complete_json("sys", "user", {"type": "object"}) == {"x": 1}

@pytest.mark.parametrize("cls", [GeminiClient, OpenAICompatibleClient])
def test_complete_json_retries_once_on_bad_json(cls):
    c = _client_with(cls, ["not json", '{"x": 2}'])
    assert c.complete_json("sys", "user", {"type": "object"}) == {"x": 2}
    assert c._calls["n"] == 2

@pytest.mark.parametrize("cls", [GeminiClient, OpenAICompatibleClient])
def test_complete_text_returns_raw_string(cls):
    c = _client_with(cls, ["<IDENT>tagged</IDENT> text"])
    assert c.complete_text("sys", "user") == "<IDENT>tagged</IDENT> text"

def test_select_client_class_maps_providers():
    assert select_client_class("openai") is OpenAICompatibleClient
    assert select_client_class("openrouter") is OpenAICompatibleClient
    assert select_client_class("gemini") is GeminiClient
    assert select_client_class("google") is GeminiClient
    with pytest.raises(ValueError):
        select_client_class("bogus")
