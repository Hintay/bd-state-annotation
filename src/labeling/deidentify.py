"""Demo runner: de-identify a post by tagging PII spans (returns tagged text)."""
from pathlib import Path
from src.prompts_loader import load_prompt

def run(client, input_path: str) -> str:
    text = Path(input_path).read_text(encoding="utf-8").strip()
    system_prompt = load_prompt("deidentify")
    return client.complete_text(system_prompt, text)

def main():
    from src.llm_client import make_client
    print(run(make_client(), "data/demo_synthetic/post_pii.txt"))
