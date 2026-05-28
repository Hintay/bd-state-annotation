from src.labeling.verify_patients import run
from src.schemas import PatientVerdict

class _FakeClient:
    def __init__(self, payload): self._payload = payload
    def complete_json(self, system_prompt, user_prompt, response_schema):
        assert "user_demo" in user_prompt
        return self._payload

def test_run_returns_schema_valid_dict():
    fake = _FakeClient({
        "author_name": "user_demo", "verification_status": "verified", "confidence": 0.92,
        "diagnosis_type": "BD_II",
        "diagnosis_evidence": [{"type": "explicit_diagnosis", "post_id": "v1",
                                "quote": "official bipolar II diagnosis", "interpretation": "clinical dx"}],
        "evidence_post_count": 3, "exclusion_flags": [], "reasoning": "dx + meds across 3 posts"})
    out = run(fake, "data/demo_synthetic/user_verify.json")
    PatientVerdict(**out)
    assert out["verification_status"] == "verified"
