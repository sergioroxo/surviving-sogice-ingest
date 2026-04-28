# SurvivingSOGICE — Local Python Runner Architecture v1.0

**Decision date:** April 2026  
**Status:** ADOPTED — supersedes Vercel-centric approach for local ingestion pipeline  
**Applies to:** Phase 0-G preprocessing scripts, local runner pipeline, embedding layer, local model stack  
**Companion documents:** `IMPLEMENTATION_PLAN_v1.0.md` · `PRD_v3.1.md` · `SANITY_SCHEMA_v1.0.md`

---

## Architecture Decision

**Option 2 adopted: Local Python runner (CLI first, local web UI second).**

All meaningful logic (Docling, sentence-transformers/qwen3-embedding, Claude SDK, Sanity client, Ollama) is Python-native. A native Mac wrapper (SwiftUI, Tauri, Electron) would be a shell calling Python subprocess — adds build complexity, signing requirements, and a second codebase without gaining capability. A Streamlit app at `localhost:8501` is functionally equivalent for a solo researcher.

This decision does not change the role of Sanity, Supabase, or Vercel. The local runner is a **producer**: intake → preprocess → embed → classify → checkpoint → upload. Sanity remains source of truth. Vercel remains the review/publish/public frontend (deferred until corpus is large enough that Sanity Studio is insufficient).

---

## A. Component Role Boundaries

| Component | Responsible for | Does NOT do |
|---|---|---|
| **Local Python runner** | Intake, preprocessing, embedding, Claude API call, human review checkpoints, local file save, Sanity upload | Publish, manage workflow state, serve public archive |
| **Python model layer** | Docling/Unstructured text extraction, sentence-transformers/qwen3 embeddings, Whisper transcription, OCR | Classification decisions (Claude's job) |
| **Sanity** | Source of truth for all records, workflow states (`unverified → verified → published`), entity registry, lexicon entries, batch tracking, binary file assets | Compute, embeddings, vector search |
| **Vercel app** | Human Review #2 (disagreements panel), lexicon browser/editor, validation batch management, publication manager, public archive, SOGICE Wikipedia | Ingestion compute, preprocessing, embeddings |
| **Supabase (pgvector)** | Embedding vectors for Phase 2 semantic search, cross-language clustering | Store document content (Sanity's job) |
| **GitHub** | Markdown docs, JSON exports per batch, application code | Binary files, live records |

---

## B. Technical Stack

```
Core language:       Python 3.11+
CLI framework:       Typer + Rich (formatted terminal output, progress bars, panels)
Local web UI:        Streamlit (Phase 0.5, served at localhost:8501)
Document parsing:    Docling (primary) + Unstructured (fallback)
URL extraction:      Trafilatura
Video/audio:         yt-dlp + faster-whisper
OCR:                 Tesseract via pytesseract
Embeddings:          Ollama qwen3-embedding:4b (default) — see Section D
LLM primary:         Anthropic Python SDK (Claude)
LLM local:           Ollama — gemma4:e4b (default), gemma4:12b (push quality) — see Section D
Data validation:     Pydantic v2 (schema enforcement on Claude's JSON output)
Sanity integration:  httpx (direct REST calls to Sanity Content API)
Supabase:            supabase-py client
Local storage:       Standard filesystem + JSON
Config:              python-dotenv (.env file, never committed)
```

---

## C. Local Model Strategy (MacBook Pro M4, 24 GB RAM)

### C.1 Embeddings

**Default:** `qwen3-embedding:4b` via Ollama
- Stronger multilingual coverage than `paraphrase-multilingual-mpnet-base-v2`
- Covers all six corpus languages (Norwegian, Portuguese, Italian, French, German, English)
- Realistic to run locally on M4 without overloading RAM
- ⚠ **Confirm output dimension before Phase 0-B** — vector column dimension in Supabase is permanent until explicit migration. Do not create the `document_embeddings` table until the exact output dimension of `qwen3-embedding:4b` is verified (run a test encode, inspect the shape of the returned vector).

**Lightweight fallback:** `embeddinggemma` via Ollama
- Use if `qwen3-embedding:4b` is too slow in practice on this machine

**Retired option (Q22 prior default):** `paraphrase-multilingual-mpnet-base-v2` (sentence-transformers, 768d)
- This was the Q22 Option B default in `IMPLEMENTATION_PLAN_v1.0.md`
- Replaced by `qwen3-embedding:4b` based on stronger multilingual performance at comparable size
- If `qwen3-embedding:4b` is unavailable or underperforms, fall back to this model (768d, `vector(768)` in Supabase)

### C.2 LLM Analysis and Tagging

**Primary:** Anthropic API (Claude `claude-sonnet-4-6` or current release)
- Handles all document classification, tagging, candidate term discovery
- Uses `ingestion-v3.1` system prompt with runtime lexicon injection
- Prompt-cached static portion reduces cost on repeat calls

**Local primary (Ollama):** `gemma4:e4b` (April 2026)
- Best fit for M4 24 GB RAM: runs without overcommitting memory
- Use for: long video transcripts (SRT files), books, and bulk documents where API quota or cost is a constraint
- Same JSON output schema as Claude path — Pydantic v2 validates both

**Local push-quality (Ollama):** `gemma4:12b`
- Use if `gemma4:e4b` output quality is insufficient for a specific document type
- Test first on your machine — run `ollama run gemma4:12b` and benchmark a sample before committing to a batch

**What NOT to start with:**
- Models 26b+ — too large for 24 GB RAM reliably
- BERTopic in MVP
- Pinecone or separate vector DB in first version

### C.3 LLM Routing Logic

The runner supports three modes, configured per session or per document:

```
--llm claude        # Claude API only (default)
--llm local         # Ollama only (gemma4:e4b by default)
--llm both          # Run both, compare outputs, flag disagreements
--llm prefer-local  # Local first; fall back to Claude if local confidence < threshold
--llm prefer-claude # Claude first; fall back to local if API unavailable
```

When `--llm both` is used, the outputs are compared field-by-field using the same disagreement logic as the Track A validation batch system. Disagreements are flagged at Checkpoint 3 (Analysis Review) so the researcher can resolve them interactively.

Long transcripts (SRT/video) and books default to `--llm local` to avoid large API context costs. The runner detects input length at Checkpoint 1 and suggests local mode if `input_length_chars > 40000`.

### C.4 Phase 2 Analysis Models

These are deferred to Phase 2 and do not affect MVP:

| Task | Model |
|---|---|
| Semantic map | UMAP (Python `umap-learn`) |
| Document clustering | HDBSCAN (Python `hdbscan`) |
| Topic modeling | BERTopic (builds on UMAP + HDBSCAN) |

---

## D. Preprocessing Strategy

### D.1 Primary: Docling

IBM Research, Apache 2.0. Best choice for this corpus:
- Research documents: PDFs, academic papers, reports, legislative submissions
- Produces clean structure-preserving Markdown — numbered sections, tables, and footnotes preserved
- Docling's Markdown feeds directly into Claude's context without further cleaning

### D.2 Fallback: Unstructured + Trafilatura

- **Unstructured:** emails, social media HTML exports, formats Docling doesn't handle
- **Trafilatura:** live URL fetching — readability extraction (strips nav, ads, boilerplate); more reliable than raw BeautifulSoup

### D.3 Video/Audio: yt-dlp + faster-whisper

- `yt-dlp` for subtitle extraction (zero transcription cost if subtitles exist)
- `faster-whisper` (CTranslate2-based Whisper) for local transcription when no subtitles
- Runs on Mac CPU/GPU; significantly faster than OpenAI's original Whisper; no API needed
- SRT/VTT timestamps stripped; clean transcript output to `extracted.txt`
- Long transcripts (>40k chars) default to `--llm local` (see C.3)

### D.4 OCR: Tesseract via pytesseract

- Handles all six corpus languages natively with language packs installed
- Feed extracted images from PDF/HTML through Tesseract
- Store OCR output separately as `ocr_images.json` for independent review

---

## E. Local File Structure

Each document gets a stable directory tied to its `doc_id` (UUID, generated at intake):

```
~/survivingsogice/corpus/{doc_id}/
├── source.pdf             # original file (or downloaded HTML)
├── source_metadata.json   # URL, access date, declared type, tier
├── extracted.md           # Docling/Unstructured markdown (primary review artifact)
├── extracted.txt          # plain text version
├── ocr_images.json        # OCR output from embedded images (if any)
├── analysis.json          # Claude's / local LLM's classification output
├── embedding.json         # vector + model name + dimension
├── review.json            # researcher's review decisions + edits
├── sanity_record.json     # final record uploaded to Sanity
└── audit.log              # timestamped event log
```

The `extracted.md` file is the primary review artifact — the researcher opens it in any editor to inspect preprocessing output before approving analysis.

`doc_id` is shared across all systems:
```
doc_id
├── Local filesystem: ~/survivingsogice/corpus/{doc_id}/
├── Sanity:           document._id = doc_id
├── Supabase:         document_embeddings.sanity_document_id = doc_id
└── GitHub export:    exports/{batch_id}/{doc_id}.json
```

---

## F. Human-in-the-Loop Checkpoints

Four interactive pauses. The runner halts at each and waits for researcher input before proceeding.

### Checkpoint 1 — Source Intake Confirmation

Before any processing:
```
SOURCE INTAKE
─────────────────────────────────────────
URL:        https://example.org/document
Title:      Detected: "Therapeutic Choice and Legislative..."
Language:   Detected: English (en)
Type:       Organization website / press release
Tier:       Auto-assigned: Tier 2
Batch:      batch-07
Doc ID:     doc_a3f8b2c1

[ proceed ] [ change tier ] [ skip ] [ abort ]
```

### Checkpoint 2 — Extracted Text Review

After Docling/Unstructured runs. Researcher sees:
- Preprocessing tool used + quality rating (`high / medium / low`)
- Character count, detected language
- The extracted Markdown (rendered or raw in terminal)
- Any OCR output from images

Researcher can approve, edit (opens `extracted.md` in default editor), override quality rating, or abort.

### Checkpoint 3 — Analysis Review

After Claude/local LLM returns classification:
```
ANALYSIS REVIEW — doc_a3f8b2c1
─────────────────────────────────────────
Type:           Pro-SOGICE  [keep] [edit]
Format:         Website-Page  [keep] [edit]
Evidence:       Organization-Claim  [keep] [edit]
Scope:          Core  [keep] [edit]
Tactic:         Policy-Resistance-Frame, Rebranding-SOGICE  [keep] [edit]
Term:           Therapeutic-Choice, SAFE-T  [keep] [edit]
Confidence:     0.87 (high)  ✓
LLM used:       claude-sonnet-4-6

Candidate terms (2):
  • "Dignity Therapy" — proposed: Policy-Resistance  [approve as draft] [dismiss]
  • "Authentic Orientation" — proposed: SSA-Rhetoric  [approve as draft] [dismiss]

Suggested actors (1):
  • "Christian Voices UK" — advocacy, GB  [approve] [dismiss]

Extractable assets (2):
  [1] legislative_quote: "The right to seek help..."  [keep] [remove]
  [2] terminology_coinage: "values-congruent therapy"  [keep] [remove]

Summary: "This document, produced by..."
  [keep] [rewrite]

[ approve all ] [ review field by field ] [ abort ]
```

If `--llm both` was used, disagreements between Claude and local LLM are highlighted in amber.

### Checkpoint 4 — Upload Confirmation

Final gate before Sanity write:
```
UPLOAD CONFIRMATION — doc_a3f8b2c1
─────────────────────────────────────────
This will write to Sanity:
  workflowStatus: unverified
  tier: 2
  10 classification fields
  2 candidate terms (as draft lexicon entries)
  1 new entity (pending researcher confirmation in Sanity)

This will also:
  • Sync embedding vector to Supabase
  • Save local backup to ~/survivingsogice/corpus/doc_a3f8b2c1/
  • Export JSON to exports/batch-07/

[ confirm upload ] [ review again ] [ save locally only ] [ abort ]
```

"Save locally only" preserves all work and defers the Sanity upload without losing anything.

---

## G. Zotero and Reference Tracking

Zotero is not a Phase 0 or Phase 1 priority. The Sanity `document` schema retains a `zotero` field (from earlier PRD versions). Options when reference tracking is needed:

1. **Manual Zotero export:** JSON export per batch from the runner is Zotero-compatible if formatted correctly — implement when needed, not at MVP
2. **Catalog document:** a `03_data/` Markdown file listing all ingested documents with `doc_id`, `source_url`, `ingested_at`, and `batch` — a lightweight alternative to a full Zotero integration for early corpus management
3. **Zotero API:** available if needed; deferred until corpus size makes it worthwhile

The per-document `source_metadata.json` (containing URL, access date, and type) and the batch JSON exports to GitHub provide sufficient tracking for Phase 0–1 without Zotero.

---

## H. Phased Build Plan

| Phase | What to build | Timeline |
|---|---|---|
| **0-A** | Sanity schema (12 types) + entity seeding | Week 1 |
| **0-B** | Supabase `document_embeddings` table — **confirm qwen3-embedding:4b dimension first** | Week 1 |
| **MVP CLI** | Python runner: `typer` + `rich`; intake → preprocess (Docling) → embed (qwen3) → Claude API → checkpoints → local save → Sanity upload | Weeks 2–3 |
| **0.5 Pilot** | Run 10–20 representative documents, calibrate confidence thresholds | Week 4 |
| **Local web UI** | Streamlit wrapper (`localhost:8501`) around same Python functions — better Markdown inspection, candidate term approval forms, JSON viewer | Weeks 5–6 |
| **Local LLM** | Ollama integration for `--llm local` / `--llm both` modes; gemma4:e4b default | After pilot |
| **Validation runner** | Track A batch validation via OpenAI API or manual export | Phase 1 |
| **Vercel app** | Full review/publish UI | Phase 1–2 |
| **Phase 2 analysis** | UMAP semantic map, HDBSCAN clustering, BERTopic, pgvector activation | After corpus is substantial |

---

## I. CLI Commands (MVP)

```bash
runner ingest <url>           # full pipeline from URL
runner ingest <file.pdf>      # full pipeline from file
runner ingest <file.srt>      # transcript pipeline (defaults --llm local)
runner ingest <file.epub>     # book pipeline (defaults --llm local)

runner ingest <url> --llm local           # force local LLM
runner ingest <url> --llm both            # run both, compare at Checkpoint 3
runner ingest <url> --tier 1              # override auto-tier
runner ingest <url> --batch batch-07      # assign to existing batch

runner review <doc_id>        # re-open Checkpoint 3 for a local document
runner upload <doc_id>        # upload a locally-saved document to Sanity
runner status                 # show pending local documents (not yet uploaded)
runner export <batch_id>      # export batch JSON to exports/{batch_id}/
```

---

## J. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Docling fails on some PDFs | Unstructured fallback + manual extraction path |
| Claude API quota exhausted | `--llm local` mode; model-agnostic export already built into `ingestion-v3.1` |
| Sanity API rate limits on bulk upload | Batch with delay; local save always happens first |
| qwen3-embedding:4b dimension unknown at plan time | **Verify dimension before Phase 0-B** — run `runner embed-test` to inspect output shape; document result, then create Supabase column |
| gemma4:12b too slow on M4 24 GB | Use `gemma4:e4b` by default; only move to 12b for specific high-value documents |
| Streamlit stateful session issues in complex pipeline | CLI always works as fallback; Streamlit wraps the same Python functions, not a separate implementation |
| Single researcher = no redundancy if Mac unavailable | Local backups in `~/survivingsogice/corpus/` + GitHub batch exports ensure no data loss |

---

## K. What This Does Not Change

- **Sanity schema** (`SANITY_SCHEMA_v1.0.md`) — unchanged; local runner writes to the same schema
- **Ingestion prompt** (`ingestion-v3.1`) — unchanged; local runner calls the same prompt
- **Validation prompt** (`validation-v3.1`) — unchanged
- **Supabase schema** (Phase 0-B) — unchanged except embedding model (see J above)
- **Vercel app** — deferred, not removed; still the target for Phase 1–2 review/publish UI
- **Phase milestones** — June 2026 and October 2026 checkpoints unchanged

---

*Companion documents: IMPLEMENTATION_PLAN_v1.0.md · PRD_v3.1.md · SANITY_SCHEMA_v1.0.md · SOGICE_Ontology_v3.0.md · TAGGING_GUIDE.md*
