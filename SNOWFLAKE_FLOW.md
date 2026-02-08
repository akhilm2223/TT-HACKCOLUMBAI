# What Snowflake Does After the JSON File Is Created

## End-to-end flow

```
Video (e.g. Recording 2026-02-07 134224.mp4)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  main.py (perception pipeline)                                   │
│  • OpenCV + MediaPipe + K2 (optional): ball, court, 2 players   │
│  • Builds in memory: court, frame_samples, shots, rallies,       │
│    behavioral_metrics, semantic_summary                          │
└─────────────────────────────────────────────────────────────────┘
    │
    ├──► Writes table_tennis_analysis.json (local file)
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  IF Snowflake env vars set (SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER):  │
│                                                                  │
│  1. Start of run: create MATCH row (MATCH_ID, VIDEO_FILE, …)     │
│  2. After JSON is built: push to Snowflake                        │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  SNOWFLAKE (single platform: storage + vectors + LLM)           │
│                                                                  │
│  A. ANALYSIS_OUTPUT table                                        │
│     • FULL_ANALYSIS (VARIANT) = entire analysis dict (same as    │
│       the JSON: court, frame_level_perception, shots, rallies,   │
│       behavioral_metrics, match_context, semantic_summary)      │
│     • SEMANTIC_SUMMARY (VARCHAR) = short text summary            │
│     • SEMANTIC_VECTOR (VECTOR 768) = Cortex EMBED_TEXT_768 of    │
│       semantic_summary for similarity search                     │
│                                                                  │
│  B. Optional: Cortex coaching (--coach flag)                      │
│     • Read this match’s FULL_ANALYSIS from Snowflake             │
│     • find_similar_matches(semantic_summary) → vector search      │
│     • Build prompt (metrics + similar past matches)               │
│     • Cortex COMPLETE (e.g. llama3.1-70b) → coaching text        │
│     • Save prompt + response in COACHING_INSIGHTS                │
└─────────────────────────────────────────────────────────────────┘
```

So: the **same** data you see in `table_tennis_analysis.json` is what gets stored in Snowflake (plus an embedding and optional Cortex coaching). Nothing is lost; Snowflake is the **second copy** and the place where **reasoning** (Cortex) runs.

---

## What each Snowflake piece does

| Component | Role |
|-----------|------|
| **MATCHES** | One row per video (MATCH_ID, VIDEO_FILE, PLAYER1/2_NAME). Created at pipeline start when DB is available. |
| **ANALYSIS_OUTPUT** | One row per match: full JSON in `FULL_ANALYSIS`, text in `SEMANTIC_SUMMARY`, and 768-d vector in `SEMANTIC_VECTOR` (from Cortex EMBED). Used as single source of truth for analytics and Cortex. |
| **TRACKING_EVENTS** | Optional frame-level events (ball/pose) if you ever call `tracking_db.add_event()` in the loop. Currently the pipeline does **not** write per-frame events; only the final analysis is pushed. |
| **MATCH_STATS** | Legacy / optional; used if you run the old StatsEngine path (e.g. from `LLMCoach.get_match_summary()`). New flow uses ANALYSIS_OUTPUT instead. |
| **COACHING_INSIGHTS** | Stores Cortex coaching: PROMPT_TEXT, LLM_RESPONSE_TEXT, PROCESSED_RESPONSE_JSON. Filled when you use `--coach` or call `CortexCoach.analyze_match()`. |
| **Cortex EMBED** | Turns `semantic_summary` into a 768-d vector so you can do “find matches similar to this one” with VECTOR_COSINE_SIMILARITY. |
| **Cortex COMPLETE** | LLM call inside Snowflake (e.g. llama3.1-70b) to generate coaching text from the analysis + similar matches. |

So: **after** the JSON file is written, Snowflake (1) stores that JSON (+ embedding) and (2) optionally runs Cortex to produce coaching and stores that in COACHING_INSIGHTS.

---

## Code locations (quick ref)

- **main.py**
  - **1091–1106:** DB setup: if `DB_AVAILABLE`, create `TrackingDB`, connect, create match row (`match_id`).
  - **1626–1653:** After writing the JSON: if `tracking_db` and `match_id` exist, call `tracking_db.db.insert_full_analysis(match_id, analysis)` then optionally run Cortex coach and print insight.
- **modules/snowflake_db.py**
  - **insert_full_analysis:** MERGE into ANALYSIS_OUTPUT (FULL_ANALYSIS, SEMANTIC_SUMMARY, SEMANTIC_VECTOR via Cortex EMBED).
  - **find_similar_matches:** Vector similarity search.
  - **cortex_complete:** Call Cortex COMPLETE for LLM text.
  - **get_analysis:** Read FULL_ANALYSIS for a match_id.
- **modules/llm_coach.py (CortexCoach)**
  - **analyze_match(match_id):** Load analysis from Snowflake → similar matches → build prompt → Cortex COMPLETE → save to COACHING_INSIGHTS.

---

## Is it good?

**Yes, with a few caveats.**

**Strengths**
- Clear split: perception in Python, storage + vectors + LLM in Snowflake.
- One source of truth: the same analysis dict that’s in the JSON is in ANALYSIS_OUTPUT.
- Vector search and Cortex run inside Snowflake (no extra DB or API for embeddings/LLM).
- Graceful fallback: if Snowflake isn’t configured, pipeline still runs and writes JSON; only the push and coaching are skipped.
- Typo fix applied: `tracking_db = None` (not `track_db`) when connect fails, so no bad state.
- `.gitignore` includes `.env`, so credentials aren’t committed.

**Things to be aware of**
1. **TRACKING_EVENTS** are not filled by the current main loop (no `add_event()` calls). Only the final analysis is pushed. So TRACKING_EVENTS is there for future or other use.
2. **Cortex** (EMBED + COMPLETE) requires Snowflake Cortex to be enabled and the ANALYSIS_OUTPUT table (and views/functions in `setup_snowflake.sql`) to exist. If the SQL hasn’t been run in your Snowflake account, `insert_full_analysis` or coaching can fail.
3. **Video path:** The terminal suggested `Recording 2026-02-05 165944.mp4`; your default in main is `Videos/Recording 2026-02-07 134224.mp4`. Use `--video "path/to/video.mp4"` to match the file you want.

**Summary**
- **What Snowflake does after the JSON:** Stores the full analysis (and its embedding), and optionally runs Cortex to generate and store coaching. The JSON file and Snowflake both hold the same logical data; Snowflake adds storage, search, and LLM.
- **Verdict:** The design is good and consistent; run `setup_snowflake.sql` in Snowflake, set `.env`, and use `--coach` when you want Cortex coaching.
