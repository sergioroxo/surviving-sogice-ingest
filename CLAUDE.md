# SurvivingSOGICE — Session Context

PhD research archive studying SOGICE (Sexual Orientation and Gender Identity Change Efforts) in Europe. Ingests documents, classifies them with Claude, builds a living lexicon, and ultimately publishes a public archive. Stack: local Python runner → Sanity (source of truth) → Supabase (vectors) → Vercel (review/publish UI, deferred).

---

## Architecture (settled)

**Option 2: Local Python CLI + Streamlit UI.** All compute is local. The runner is in `runner/`. Sanity and Vercel roles are unchanged.

Key docs:
- `01_project_docs/ARCHITECTURE_LOCAL_RUNNER_v1.0.md` — architecture decision, role boundaries, model stack, checkpoints
- `01_project_docs/IMPLEMENTATION_PLAN_v1.0.md` — full phase plan (written for Vercel but phases 0-A/0-B/0-G and all prompt/schema tasks are still accurate)
- `02_working_tools/Claude_Ingestion_Prompt.md` — ingestion-v3.1 system prompt + exact JSON output schema
- `00_infrastructure/SANITY_SCHEMA_v1.0.md` — all 12 Sanity content types
- `00_infrastructure/Entity_Registry_v1.1.md` — seed data for persons, orgs, laws, events

---

## Local Model Stack (MacBook Pro M4, 24 GB RAM)

| Task | Default | Alternative |
|---|---|---|
| Embeddings | `qwen3-embedding:4b` via Ollama | `embeddinggemma` (lighter) |
| Local LLM analysis | `gemma4:e4b` via Ollama | `gemma4:12b` (push quality) |
| Primary LLM | Claude API (`claude-sonnet-4-6`) | — |
| Transcription | `faster-whisper` (local) | — |
| OCR | Tesseract | — |
| Phase 2 semantic map | UMAP + HDBSCAN + BERTopic | — |

Long transcripts (SRT, books >40k chars) default to `--llm local`.

---

## Open Questions

| # | Question | Blocks |
|---|---|---|
| ~~**Q22**~~ | ~~Verify `qwen3-embedding:4b` output dimension~~ — **RESOLVED: 2560d** | ~~Phase 0-B~~ unblocked |
| Q14 | JUST CHANGE™ ↔ i-Doc integration method | Phase 4 October build |
| Q18 | Testimony removal formal protocol | Phase 3 publication |

**Q22 resolved (April 2026):** `qwen3-embedding:4b output dimension = 2560d`  
Use `vector(2560)` in Supabase. Verified with `python -m runner embed-test`.

---

## Build Checklist

### Phase 0-A — Sanity Schema
- [ ] Create Sanity project (EU/Norwegian region)
- [ ] Implement all 12 content types from `SANITY_SCHEMA_v1.0.md`
- [ ] Add `accessibleDefinition` field to `lexiconEntry` type
- [ ] Configure researcher + intern roles
- [ ] Seed persons and organizations from `Entity_Registry_v1.1.md` (~15 persons, ~50 orgs)
- [ ] Seed laws and events (~12 laws, ~10 events)
- [ ] Seed `legalDefinition` records from `SOGICE_Ontology_v3.0.md` Part V (9 records)
- [ ] Seed `exclusionClause` records (6 records, linked to legalDefinitions)
- [ ] Test round-trip: create a document record, verify all fields persist
- [ ] Export seed JSON snapshot to `03_data/sanity_seed_YYYY-MM-DD.json`

### Phase 0-B — Supabase Schema
- [x] **Q22 resolved** — `qwen3-embedding:4b` = **2560d** → use `vector(2560)`
- [ ] Create Supabase project (EU region)
- [ ] Enable pgvector extension
- [ ] Create `document_embeddings` table with correct-dimension vector column
- [ ] Create ivfflat index
- [ ] Test: ingest one document → verify null-vector row appears

### MVP CLI Runner (`runner/`)
- [x] Project skeleton (`main.py`, `config.py`, `models/`, `pipeline/`, `clients/`)
- [x] Pydantic models for ingestion-v3.1 output schema
- [x] `requirements.txt` + `.env.example`
- [ ] **`pipeline/intake.py`** — URL/file detection, doc_id generation, Wayback Machine check
- [ ] **`pipeline/preprocess.py`** — Docling (PDF), Trafilatura (URL), yt-dlp + faster-whisper (video)
- [ ] **`pipeline/embed.py`** — Ollama qwen3-embedding:4b call, save to `embedding.json`
- [ ] **`pipeline/analyze.py`** — Claude API call + Ollama fallback, Pydantic validation of response
- [ ] **`pipeline/review.py`** — Rich terminal checkpoints 1–4
- [ ] **`pipeline/upload.py`** — Sanity REST write + Supabase row insert
- [ ] **`clients/sanity.py`** — httpx Sanity Content API client
- [ ] **`clients/supabase.py`** — supabase-py client wrapper
- [ ] End-to-end test: one URL through full pipeline

### Phase 0.5 — Pilot Batch
- [ ] Run 10–20 documents covering all 6 languages + all tiers
- [ ] Calibrate confidence thresholds (baseline: high ≥0.85, medium 0.70–0.84, low <0.70)
- [ ] Calibrate validation triggers
- [ ] Test lexicon Track B (approve ≥5 candidate terms)
- [ ] Test model-agnostic export + reimport

### Phase 1 — Full Ingestion Pipeline
- [ ] Validation batch system
- [ ] Review queue (`/review/queue` on Vercel or Streamlit)
- [ ] Lexicon Track B UI
- [ ] JSON export to GitHub per batch

### Streamlit Web UI (Phase 0.5 parallel)
- [ ] `runner/app.py` — Streamlit wrapper around same pipeline functions
- [ ] Markdown preview tab
- [ ] Candidate term approval forms
- [ ] JSON diff viewer (Claude vs local LLM)

### Deferred
- [ ] Vercel app (Phase 1–2)
- [ ] Phase 2: UMAP / HDBSCAN / BERTopic / pgvector activation
- [ ] Phase 3: Public archive + SOGICE Wikipedia
- [ ] Phase 4: JUST CHANGE™ + i-Doc

---

## Runner Quick Reference

```bash
# Install
cd runner && pip install -r requirements.txt
cp .env.example .env  # fill in API keys

# Use
python -m runner ingest https://example.org/document
python -m runner ingest document.pdf --tier 2
python -m runner ingest recording.mp4 --llm local
python -m runner ingest document.pdf --llm both   # Claude + Ollama, compare outputs

python -m runner status                  # show locally saved, not yet uploaded
python -m runner upload <doc_id>         # push a saved document to Sanity
python -m runner export batch-07         # export batch JSON to exports/batch-07/

# Verify embedding dimension (do this before Phase 0-B)
python -m runner embed-test
```

---

## File Map

```
runner/
├── main.py               # Typer CLI entry point — all commands
├── config.py             # .env loading, Config dataclass
├── models/
│   └── document.py       # Pydantic models for ingestion-v3.1 output schema
├── pipeline/
│   ├── intake.py         # Checkpoint 1: source detection, doc_id, Wayback
│   ├── preprocess.py     # Checkpoint 2: Docling / Trafilatura / yt-dlp / Whisper
│   ├── embed.py          # qwen3-embedding:4b via Ollama
│   ├── analyze.py        # Claude API + Ollama routing, Pydantic validation
│   ├── review.py         # Checkpoints 1–4 Rich terminal UI
│   └── upload.py         # Sanity write + Supabase insert + local save
└── clients/
    ├── sanity.py         # httpx Sanity Content API client
    └── supabase.py       # supabase-py wrapper

00_infrastructure/        # Entity registry, lexicon, ontology, Sanity schema
01_project_docs/          # PRD, implementation plan, architecture decision
02_working_tools/         # Ingestion + validation prompts, tagging guide
03_data/                  # Seed data exports, term additions
exports/                  # Per-batch JSON exports (gitignored if large)
```

---

*Active branch: `claude/review-architecture-70CUm`*
