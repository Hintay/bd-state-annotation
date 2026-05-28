from pathlib import Path
from src.prompts_loader import load_prompt, PROMPTS_DIR

def test_load_prompt_returns_nonempty_string():
    text = load_prompt("batch_single")
    assert isinstance(text, str) and len(text) > 100

def test_loaded_prompt_has_no_frontmatter():
    for name in ["batch_single", "trend_analysis", "patient_verification", "deidentify"]:
        text = load_prompt(name)
        assert not text.lstrip().startswith("---"), f"{name} still has frontmatter"

def test_deidentify_has_no_yada_citation():
    text = load_prompt("deidentify")
    assert "Yada" not in text

def test_all_prompt_files_exist():
    for name in ["batch_single", "trend_analysis", "patient_verification", "deidentify"]:
        assert (PROMPTS_DIR / f"{name}.md").exists()
