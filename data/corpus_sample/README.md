# Corpus Sample

**This is a small illustrative sample (4 users) drawn from the bipolar-disorder
(BD) labeled Reddit corpus. The full corpus is NOT included in this repository.**

The four users were selected to span different mood trajectories (depressive-
predominant/stable, hypomanic with movement toward mania, mixed depressive/manic,
and full-range fluctuating).

## De-identification and re-identification protection

All post text has been de-identified with `prompts/deidentify.md`; detected PII
spans are replaced with `[CATEGORY]` placeholders (e.g. `[IDENT]`, `[QUASI]`). To
prevent metadata-based re-identification, the following transformations are also
applied:

- **Author** → pseudonym `user_01` … `user_04`.
- **Post ID** → local index (`u01_p03`); the real Reddit ID is dropped so posts
  cannot be fetched back.
- **Time** → relative `day` offset from each user's first sampled post; absolute
  dates are removed. This preserves 14-day windowing while blocking time-plus-
  subreddit lookup.
- **Absolute dates in annotation free-text** (`trend_summary`, change-point
  `event`) that fall inside the period's window are converted to the same
  relative `day_N` offset; any date outside the window (or too coarse to place)
  is masked to `[DATE]`. Change-point `date` is likewise a relative `day_N`.

Subreddit names and clinical content (medications, diagnoses, symptoms) are
preserved, as they are not identifying and are essential to the annotation task.

## Files

- `posts.jsonl` — one de-identified post per line:
  `{author, post_id, day, subreddit, kind, text}`.
- `annotations_single.jsonl` — per-post state labels, keyed by `post_id`:
  `{post_id, state, opposite_pole_symptoms, specifiers, confidence, reasoning}`.
- `annotations_period_14d.jsonl` — 14-day period-level trend labels, keyed by
  `author` + window: `{author, window_start_day, window_end_day, dominant_state,
  opposite_pole_symptoms, specifiers, trend_direction, trend_summary,
  change_points, confidence}`.

`state` / `dominant_state` ∈ {MANIC, HYPOMANIC, DEPRESSIVE, STABLE, UNCERTAIN}.
