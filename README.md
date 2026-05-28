# Longitudinal State Annotation for Bipolar Disorder

Code and a small de-identified data sample accompanying our submission on a
few-shot prompt-based LLM method for longitudinal mood-state annotation of
Reddit posts for bipolar disorder (BD) research. External validation uses the
BD-Risk dataset (Lee et al., NAACL 2024).

## Overview

The method annotates Reddit posts at two temporal granularities, grounded in
DSM-5 episode criteria and requiring no task-specific fine-tuning:

- **Per-post mood state**: MANIC / HYPOMANIC / DEPRESSIVE / STABLE (with
  UNCERTAIN as a defensive fallback).
- **14-day period trend**: dominant state + trend direction (NO_TREND,
  FLUCTUATING, TOWARDS_DEPRESSION, TOWARDS_MANIA) + DSM-5 specifiers + change
  points.

Two supporting prompts handle BD-patient verification (is the author a
self-identified, diagnosed BD patient?) and PII de-identification of post text.

## Repository Layout

```
.
├── README.md
├── LICENSE
├── main.py                       # CLI: python main.py {single|trend|verify|deid}
├── pyproject.toml                # uv-based; requirements.txt as fallback
├── requirements.txt
├── .env.example                  # provider + API key configuration
├── prompts/
│   ├── batch_single.md           # per-post state classification
│   ├── trend_analysis.md         # 14-day period trend
│   ├── patient_verification.md   # BD-patient verification
│   └── deidentify.md             # PII de-identification
├── src/
│   ├── llm_client.py             # minimal two-provider client (OpenAI-compatible / Gemini)
│   ├── prompts_loader.py
│   ├── schemas.py                # pydantic output contracts
│   └── labeling/
│       ├── label_single.py
│       ├── label_trend.py
│       ├── verify_patients.py
│       └── deidentify.py
├── data/
│   ├── demo_synthetic/           # fully synthetic demo inputs (no real PII)
│   └── corpus_sample/            # 4 de-identified users from the BD corpus (sample only)
└── tests/                        # hermetic unit tests (no API/SDK required)
```

## Setup

- Python 3.11+
- `uv sync` (or `pip install -r requirements.txt`)
- `cp .env.example .env` and configure a provider:
  - **OpenAI-compatible** (default; OpenRouter / OpenAI / Azure): set
    `LLM_PROVIDER=openai`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL_NAME`.
  - **Google AI official**: set `LLM_PROVIDER=gemini`, `GEMINI_API_KEY`, and
    optionally `GEMINI_MODEL_NAME`.

The reported results use Gemini 3.1 Pro.

## Quick Start — Run the Demo

Each command runs one prompt on a fully synthetic input under
`data/demo_synthetic/` and prints the result:

```bash
python main.py single   # per-post state classification
python main.py trend    # 14-day period trend
python main.py verify   # BD-patient verification
python main.py deid     # PII de-identification (prints tagged text)
```

## Prompts

| File | Role | Output |
|---|---|---|
| `prompts/batch_single.md` | Per-post state classification | `{state, opposite_pole_symptoms, specifiers, confidence, reasoning}` |
| `prompts/trend_analysis.md` | 14-day period trend | `{dominant_state, trend_direction, opposite_pole_symptoms, specifiers, trend_summary, change_points, confidence}` |
| `prompts/patient_verification.md` | BD-patient verification | `{verification_status, confidence, diagnosis_type, diagnosis_evidence, evidence_post_count, exclusion_flags, reasoning}` |
| `prompts/deidentify.md` | PII de-identification | tagged text with `<IDENT>` / `<QUASI>` / `<CONTACT>` / `<LINK>` / `<PID>` spans |

## Data

- `data/demo_synthetic/` — fully synthetic inputs for the runnable demo (no real
  PII); the synthetic examples mirror those documented in the prompts.
- `data/corpus_sample/` — 4 users from the BD-labeled corpus, de-identified via
  the de-identify prompt with metadata re-identification protection. **Sample
  only**; the full corpus is not included here. See
  `data/corpus_sample/README.md`.
- The BD-Risk dataset (used for external validation) is NOT included; obtain it
  through the original authors' request-access process (Lee et al., NAACL 2024).

## Ethics

The corpus was collected under institutional ethics approval (IRB no. 25-188).
Released posts are de-identified; subreddit names, medications, diagnoses, and
clinical content are preserved because they are essential to the task and are not
identifying. Patient verification is LLM-based and does not constitute a clinical
diagnosis.

## License

MIT — see `LICENSE`.

## Citation

If you use this code or sample, please cite our submission:

> Jiefeng Lin and Shuntaro Yada. *Few-Shot Prompt-Based Longitudinal Mood-State
> Analysis of Bipolar Disorder on Social Media.* 2026. (Under review.)
