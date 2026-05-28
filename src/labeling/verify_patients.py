"""Demo runner: verify whether a user is a genuinely diagnosed BD patient."""
import json
from pathlib import Path
from src.prompts_loader import load_prompt
from src.llm_client import unwrap_one
from src.schemas import PatientVerdict

SCHEMA = PatientVerdict.model_json_schema()

def run(client, input_path: str) -> dict:
    user = json.loads(Path(input_path).read_text(encoding="utf-8"))
    system_prompt = load_prompt("patient_verification")
    lines = [f'({p["post_id"]}) {p["text"]}' for p in user["posts"]]
    user_prompt = f'author_name: {user["author_name"]}\n\n' + "\n".join(lines)
    result = unwrap_one(client.complete_json(system_prompt, user_prompt, response_schema=SCHEMA))
    PatientVerdict(**result)
    return result

def main():
    from src.llm_client import make_client
    out = run(make_client(), "data/demo_synthetic/user_verify.json")
    print(json.dumps(out, indent=2, ensure_ascii=False))
