"""Demo runner: assess a user's 14-day period for mood trend."""
import json
from pathlib import Path
from src.prompts_loader import load_prompt
from src.schemas import TrendLabel

SCHEMA = TrendLabel.model_json_schema()

def run(client, input_path: str) -> dict:
    period = json.loads(Path(input_path).read_text(encoding="utf-8"))
    system_prompt = load_prompt("trend_analysis")
    lines = [f'[day {p["day"]}] ({p["post_id"]}) {p["text"]}' for p in period["posts"]]
    user_prompt = f'Period id: {period["id"]}\n\n' + "\n".join(lines)
    result = client.complete_json(system_prompt, user_prompt, response_schema=SCHEMA)
    TrendLabel(**result)
    return result

def main():
    from src.llm_client import GeminiClient
    out = run(GeminiClient(), "data/demo_synthetic/user_period.json")
    print(json.dumps(out, indent=2, ensure_ascii=False))
