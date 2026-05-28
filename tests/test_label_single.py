from src.labeling.label_single import run
from src.schemas import SinglePostLabel

class _FakeClient:
    def __init__(self, payload): self._payload = payload
    def complete_json(self, system_prompt, user_prompt, response_schema):
        assert "demo_single_01" in user_prompt
        return self._payload

def test_run_returns_schema_valid_dict(tmp_path):
    fake = _FakeClient({
        "id": "demo_single_01", "state": "HYPOMANIC",
        "opposite_pole_symptoms": [], "specifiers": [],
        "confidence": "High", "reasoning": "impulsive spending + reduced sleep"})
    out = run(fake, "data/demo_synthetic/single.json")
    SinglePostLabel(**out)            # raises if invalid
    assert out["state"] == "HYPOMANIC"
