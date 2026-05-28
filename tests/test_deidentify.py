from src.labeling.deidentify import run

class _FakeClient:
    def __init__(self, payload): self._payload = payload
    def complete_text(self, system_prompt, user_prompt):
        assert "Dr. Harlow" in user_prompt
        return self._payload

def test_run_returns_tagged_text():
    tagged = ("My psychiatrist <IDENT>Dr. Harlow</IDENT> at <QUASI>the Brightwater Clinic "
              "in Fairmont</QUASI> started me on lithium last month. I'm a "
              "<QUASI>34-year-old teacher in Lakeside</QUASI> and I finally feel stable.")
    fake = _FakeClient(tagged)
    out = run(fake, "data/demo_synthetic/post_pii.txt")
    assert isinstance(out, str)
    assert "<IDENT>" in out and "lithium" in out
