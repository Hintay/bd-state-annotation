from src.labeling.label_trend import run
from src.schemas import TrendLabel

class _FakeClient:
    def __init__(self, payload): self._payload = payload
    def complete_json(self, system_prompt, user_prompt, response_schema):
        assert "u_d8" in user_prompt
        return self._payload

def test_run_returns_schema_valid_dict():
    fake = _FakeClient({
        "id": "demo_period_01", "dominant_state": "MANIC",
        "opposite_pole_symptoms": [], "specifiers": ["with_mixed_features"],
        "trend_direction": "TOWARDS_MANIA", "trend_summary": "stable -> hypomanic -> manic",
        "change_points": [{"date": "day_5", "event": "activation", "pre_state": "STABLE", "post_state": "HYPOMANIC"}],
        "confidence": 0.95})
    out = run(fake, "data/demo_synthetic/user_period.json")
    TrendLabel(**out)
    assert out["trend_direction"] == "TOWARDS_MANIA"
