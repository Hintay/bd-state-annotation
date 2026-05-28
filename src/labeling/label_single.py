"""Demo runner: classify a single post's mood state."""
import json
from pathlib import Path
from src.prompts_loader import load_prompt
from src.llm_client import unwrap_one
from src.schemas import SinglePostLabel

SCHEMA = SinglePostLabel.model_json_schema()

def run(client, input_path: str) -> dict:
    post = json.loads(Path(input_path).read_text(encoding="utf-8"))
    system_prompt = load_prompt("batch_single")
    user_prompt = f'Post id: {post["id"]}\n\n{post["text"]}'
    result = unwrap_one(client.complete_json(system_prompt, user_prompt, response_schema=SCHEMA))
    SinglePostLabel(**result)          # validate
    return result

def main():
    from src.llm_client import make_client
    out = run(make_client(), "data/demo_synthetic/single.json")
    print(json.dumps(out, indent=2, ensure_ascii=False))
