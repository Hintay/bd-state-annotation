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
    return SinglePostLabel(**result).model_dump()   # validate + normalize (drop extra keys)

def main():
    from src.llm_client import make_client
    from src.render import print_json_result
    print_json_result(run(make_client(), "data/demo_synthetic/single.json"))
