import json
import pytest
from src.llm_client import strip_additional_properties, GeminiClient

def test_strip_additional_properties_recursive():
    schema = {"type": "object", "additionalProperties": False,
              "properties": {"a": {"type": "object", "additionalProperties": False,
                                   "properties": {"b": {"type": "string"}}}}}
    cleaned = strip_additional_properties(schema)
    assert "additionalProperties" not in cleaned
    assert "additionalProperties" not in cleaned["properties"]["a"]

def _client_with(outputs):
    c = GeminiClient.__new__(GeminiClient)     # bypass __init__ (no SDK / no API key)
    c.model_name = "fake"
    seq = list(outputs); calls = {"n": 0}
    def fake_generate(system_prompt, user_prompt, response_schema=None):
        i = calls["n"]; calls["n"] += 1; return seq[i]
    c._generate = fake_generate
    c._calls = calls
    return c

def test_complete_json_parses_valid():
    c = _client_with(['{"x": 1}'])
    assert c.complete_json("sys", "user", {"type": "object"}) == {"x": 1}

def test_complete_json_retries_once_on_bad_json():
    c = _client_with(["not json", '{"x": 2}'])
    assert c.complete_json("sys", "user", {"type": "object"}) == {"x": 2}
    assert c._calls["n"] == 2

def test_complete_text_returns_raw_string():
    c = _client_with(["<IDENT>tagged</IDENT> text"])
    assert c.complete_text("sys", "user") == "<IDENT>tagged</IDENT> text"
