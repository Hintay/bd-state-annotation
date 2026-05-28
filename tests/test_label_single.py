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

def test_run_unwraps_batch_list_and_drops_extra_keys():
    # Batch-oriented prompts may return a JSON array; the runner unwraps to the
    # first item, validates, and normalizes (extra keys dropped via model_dump).
    fake = _FakeClient([{
        "id": "demo_single_01", "state": "STABLE",
        "opposite_pole_symptoms": [], "specifiers": [],
        "confidence": "Low", "reasoning": "ok", "EXTRA": "should be dropped"}])
    out = run(fake, "data/demo_synthetic/single.json")
    assert out["state"] == "STABLE"
    assert "EXTRA" not in out
