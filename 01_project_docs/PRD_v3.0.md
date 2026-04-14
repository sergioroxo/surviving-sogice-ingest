# SurvivingSOGICE — Product Requirements Document v3.0

**Project:** SurvivingSOGICE
**Institution:** University of Bergen — INFOMEDIA / Center for Digital Narrative
**Researcher:** Sérgio Galvão Roxo
**Public URL:** survivingsogice.eu
**Document status:** Living document — updated per session
**Last updated:** April 2026
**Version:** 3.0 (supersedes PRD v2.0 and PRD v1.0)
**June 2026 milestone:** CDN Pride Bergen work-in-progress showing
**October 2026 milestone:** Full exhibition

---

## Table of Contents

1. [Core Platform Concept](#1-core-platform-concept)
2. [System Architecture](#2-system-architecture)
3. [Pipeline — Five Phases](#3-pipeline--five-phases)
4. [Preprocessing Layer](#4-preprocessing-layer)
5. [LLM Ingestion Layer](#5-llm-ingestion-layer)
6. [Dual-LLM Triangulation — Methodological Design](#6-dual-llm-triangulation--methodological-design)
7. [Human Review Layer](#7-human-review-layer)
8. [Token Economy and Payload Design](#8-token-economy-and-payload-design)
9. [Experience Modules](#9-experience-modules)
10. [WebXR and i-Doc Architecture](#10-webxr-and-i-doc-architecture)
11. [Ontology — Summary and Cross-Reference](#11-ontology--summary-and-cross-reference)
12. [Lexicon — Summary and Cross-Reference](#12-lexicon--summary-and-cross-reference)
13. [Entity Model — Six Entity Types](#13-entity-model--six-entity-types)
14. [JSON Schema — Document Record](#14-json-schema--document-record)
15. [Testimony as a Separate Content Type](#15-testimony-as-a-separate-content-type)
16. [Landmark Events and Named Scandals](#16-landmark-events-and-named-scandals)
17. [Scope Logic — What Goes In and Why](#17-scope-logic--what-goes-in-and-why)
18. [URL Harvesting and Web Archiving](#18-url-harvesting-and-web-archiving)
19. [Priority Scoring System](#19-priority-scoring-system)
20. [Storage, Backup, and Preservation](#20-storage-backup-and-preservation)
21. [Users and Permissions](#21-users-and-permissions)
22. [Non-Functional Requirements](#22-non-functional-requirements)
23. [Intern Checklist](#23-intern-checklist)
24. [Phase Structure and Milestones](#24-phase-structure-and-milestones)
25. [Document Inventory](#25-document-inventory)
26. [Open Questions](#26-open-questions)

---

## 1. Core Platform Concept

SurvivingSOGICE is not a traditional archive. It is a **creative input dataset** that feeds multiple digital storytelling outputs, designed to be navigated as an experience — closer to an i-Doc or interactive web documentary than a database interface.

The platform operates on three simultaneous registers:

**Archive layer** — a tagged, structured corpus of pro-SOGICE and anti-SOGICE documents, with provenance, network mapping, and metadata. This is the analytical backbone of the PhD research. Each document record includes an AI-generated research summary and links to related entities, terms, and other documents — building toward a navigable SOGICE knowledge base.

**Lexicon layer** — a living glossary of SOGICE terminology, euphemisms, slurs, pseudo-diagnostics, and coded language across all relevant world languages. Structured as interconnected encyclopedia entries: each term links to related terms, source documents, actors who use it, and the legal instruments that define or contest it. The lexicon functions as a **SOGICE Wikipedia** — a publicly browsable, internally linked reference. Full content in `SOGICE_Lexicon_v2.0.md`.

**Experience layer** — interconnected interactive digital storytelling modules, navigable as a unified environment styled as a retro computer/OS shell. Individual modules are "applications" that open and link to each other.

The primary navigation metaphor is **an old computer interface** — the user moves through it as if exploring a machine that holds suppressed information. Some modules open into immersive 360/WebXR environments; most are screen-based. The system is designed to scale across mobile, desktop, and WebXR.

**Non-negotiable design principle across all experience modules:** darkness is earned through compliance, not announced. The platform should feel like a polished commercial product at the start. Horror accumulates through mechanism.

---

## 2. System Architecture

### 2.1 Core Principle — Three Layers, Strict Boundaries

The system is structured around three distinct layers with strict role separation. No layer performs the work of another.

**Layer 1 — Preprocessing (local machine, deterministic).** Cleans and structures raw data. Reduces LLM cost and token size. Performs NO interpretation, classification, or tagging.

**Layer 2 — LLM Ingestion (application layer, probabilistic).** Generates structured metadata, assigns tags and summaries, produces schema-compliant JSON, extracts creative assets. Two LLMs operate sequentially: Claude for primary ingestion, ChatGPT for validation and supplementary extraction. Human review occurs between and after both.

**Layer 3 — Human Review (researcher-controlled, authoritative).** Validates and corrects outputs. Resolves ambiguity, disagreements, and boundary cases. Is the final authority on all interpretation. No AI-generated content reaches the public archive without human verification.

### 2.2 Core Stack

**Application Layer — Vercel**

Single hosted web application providing:
- Ingestion interface (document input, Claude analysis, tag review)
- Validation interface (ChatGPT cross-check, disagreement review)
- Human review interface (browse, filter, confirm/reject/modify, publish)
- Vocabulary browser and editor
- **Automatic Wayback Machine integration** — when a URL is submitted in the ingestion field, the app queries the Archive.org Availability API; if archived, stores the Wayback URL; if not, triggers a save request to `web.archive.org/save/`
- Export functions (JSON, CSV)

**Data Layer — Sanity.io (single source of truth)**

Central database storing all record types:
- Documents (source records with tags, metadata, provenance)
- Testimonies (linked to source documents, consent-controlled)
- Entities (Person, Organization, Law/Policy, Event, LegalDefinition, ExclusionClause)
- Lexicon entries (term definitions with multilingual variants, interlinked)
- Extractable assets (prayers, scripts, quotes, statistics)
- **Binary files** — PDFs, HTML snapshots, video files, images stored as Sanity file assets

Sanity functions as BOTH the working database and the public archive backend. Real-time collaboration handles 2–3 concurrent users natively.

**Workflow states (required from day one):**
- `unverified` — AI-generated output, no human review yet
- `in_progress` — human reviewer has opened the record
- `verified` — record checked, tags confirmed or corrected
- `published` — visible on public archive

All AI-generated output enters Sanity with `workflowStatus: "unverified"`. Nothing with `unverified` status appears on the public archive.

**Backup Layer — GitHub**

Version-controlled backup of:
- Project markdown documents (ontology, lexicon, PRD, tagging guides)
- Folder structure and configuration
- JSON exports of Sanity records (per batch or daily)
- Python preprocessing scripts
- Application code

GitHub does NOT store binary files (PDFs, HTML snapshots, video). Those live in Sanity.

**Preservation Layer — Internet Archive**

- Every URL archived via Wayback Machine (triggered automatically by the Vercel app on URL submission)
- Large video files (documentaries, recorded testimonies) uploaded to Internet Archive directly — free, citable, permanent
- References stored in Sanity as URLs

### 2.3 Architecture Diagram

```
[Local Machine]                    [Vercel App]                     [Sanity.io]
     |                                  |                                |
     | Unstructured.io                  |                                |
     | yt-dlp / Whisper                 |                                |
     | Text cleaning                    |                                |
     |                                  |                                |
     +------ cleaned text + metadata -->|                                |
                                        |                                |
                                        | URL submitted → Wayback check  |
                                        | → archive if needed            |
                                        |                                |
                                        | Claude API (primary ingestion) |
                                        | → tags, summary, terms, assets |
                                        |                                |
                                        | Human reviews Claude output -->|--- unverified
                                        | → approve/reject tags          |
                                        | → approve new terms → Lexicon  |
                                        |                                |
                                        | [Batch trigger: 20-50 docs]    |
                                        |                                |
                                        | ChatGPT API (validation +      |
                                        |   asset extraction +           |
                                        |   tag suggestions)             |
                                        |                                |
                                        | Human resolves disagreements ->|--- verified
                                        |                                |
                                        | Publish ---------------------->|--- published
                                        |                                |
                                        |                         [Public Archive]
                                        |                         survivingsogice.eu
                                        |                                |
                                        |                         [WebXR / i-Doc]
```

### 2.4 Public Archive and Lexicon

**Platform:** Next.js deployed on Vercel or UiB shared hosting. Reads from Sanity via GROQ API. Only records with `workflowStatus: "published"` are visible.

**Archive features:**
- Browse by: actor, network, country, tactic, term, cluster, document type, year
- Full-text search across all published records
- Individual document pages showing: research summary, tags, entity links, outbound URLs, Wayback link
- **AI process metadata visible on every public record** — model used, ontology version, whether human-reviewed, dual-LLM agreement status

**Lexicon features (SOGICE Wikipedia):**
- Every term links to: related terms, source documents, actors who use it, legal instruments
- Browsable by cluster, searchable by term
- Each entry page shows: definition, function, related terms, source documents, multilingual variants
- Internal linking between entries (term A's page links to term B when they are related)

**Entity pages:** For each Organization, Person, Law — profile and all connected documents.

No login required for public access.

**Hosting:** UiB institutional hosting preferred (Skeivt arkiv precedent). NREC self-hosted VM as fallback.

### 2.5 WebXR Network Visualization

Three.js / WebGL force-directed graph with multiple view modes:

| View | Description |
|---|---|
| **Network View** | Organizations, people, laws, funding sources as nodes; typed relationships as edges |
| **Country View** | Same graph filtered and clustered by geography |
| **Timeline View** | Graph animated across years; watch connections form and dissolve |
| **Map View** | Geolocated nodes on world map (D3.js / Mapbox) |
| **Semantic Map View** | Embedding-based 2D landscape via t-SNE dimensionality reduction |
| **Story / Testimony View** | Graph entered from a survivor testimony; nodes are the forces that surrounded that person |

Design references: SPLC Hate Map, Queering the Map, Magisterium AI Vector Map, Runoregi (FILTER project, University of Helsinki).

---

## 3. Pipeline — Five Phases

### Phase 0 — Discovery

- Identify and collect documents using research tools (Perplexity, library databases, OSINT toolkit)
- **URL archiving is automatic** — when a URL is entered in the Vercel app's ingestion field, the app queries the Wayback Machine API and triggers archiving if needed
- Download social media content immediately via yt-dlp (content disappears)
- File raw documents: `/corpus/raw/[YYYY-MM]/[country-code]_[actor-abbreviation]_[year]_[short-title].ext`

### Phase 1 — Preprocessing (local machine only)

Deterministic text extraction and cleaning. No classification, no tagging.

**Tools:** Unstructured.io (PDFs, HTML, reports), yt-dlp (video subtitles), Whisper/Autotekst (transcription when no subtitles exist)

**Output:** Clean text with document metadata (source URL, file type, language detected, word count, chunk boundaries).

### Phase 2 — LLM Ingestion (dual-LLM, sequential)

**Step 1 — Claude (primary ingestion):**
- Research summary (prose paragraph, 80–150 words — see §5.2)
- Classification tags (all vocabulary categories)
- Narrative register
- Scope, Landmark, Flag assignments
- Document date with confidence
- **Extractable assets** for creative practice (prayers, scripts, testimony excerpts, statistical claims, visual assets)
- Discovered terms with definitions
- Suggested new actors/networks
- Priority score (5 axes)

**Human Review #1:** Researcher/intern reviews Claude output — approves/rejects tags, approves new terms (which enter the Lexicon), approves new entities (which enter the Registry).

**Step 2 — ChatGPT (validation + supplementary extraction, on batch of 20–50 docs):**
- Tag validation — agrees/disagrees with each Claude tag
- **Tag suggestions** — proposes additional tags Claude may have missed (the lexicon is constantly growing; ChatGPT may recognize terms added since Claude's prompt was last updated)
- **Asset extraction** — identifies extractable assets for creative practice that Claude may have missed
- Disagreements with rationale
- Confidence assessment

**Step 3 — Status assignment:**
- `ready` — both LLMs agree, human has reviewed
- `needs_review` — disagreements or uncertainty
- `high_risk` — significant disagreements, sensitive content, testimony

### Phase 3 — Human Validation

Researcher resolves disagreements, finalizes all classifications, approves testimony extraction, advances to `verified`.

### Phase 4 — Publication

Final records in Sanity with `workflowStatus: "published"`. JSON exported to GitHub. Available to public archive, visualizations, experience modules.

---

## 4. Preprocessing Layer

### 4.1 Unstructured.io Integration

**Used for:** Long PDFs, reports, HTML extraction, scanned documents.
**Does:** Cleaning, chunking, section splitting, noise removal.
**Does NOT:** Classify, tag, summarize, or interpret.

Large documents (80+ pages) are chunked by Unstructured.io. Each chunk is processed by Claude separately, then synthesized into a single document record. Documents over 150 pages: process chapter by chapter.

### 4.2 Video Processing Pipeline

1. Extract subtitles (yt-dlp)
2. If missing → transcribe (Whisper / Autotekst)
3. Clean transcript (strip timestamps, formatting artifacts)
4. For long videos: chunk transcript
5. Claude processes chunks → per-chunk analysis
6. Claude synthesizes → final document record

### 4.3 Exploration Tools (Not Part of Pipeline)

NotebookLM, Gemini, Microsoft 365 Copilot — allowed for understanding complex documents and exploring patterns. NOT allowed for tagging, metadata generation, or any output that enters the ingestion pipeline directly.

---

## 5. LLM Ingestion Layer

### 5.1 Claude — Primary Ingestion

**API:** Anthropic API (claude-sonnet-4 or current equivalent)
**Cost:** ~$0.10–0.40 per analysis
**API key management:** Researcher holds key. Interns access via Vercel interface.

**System prompt architecture:** Two jobs — CLASSIFY and DISCOVER. Absolute rules enforced (exact tag strings, promotional-use-only for Terms, country = organization's country).

**Output per document — token budget:**

| Output | Est. tokens | Notes |
|---|---|---|
| Research summary | ~150–200 | Prose paragraph (§5.2) |
| Classification tags | ~100–200 | Compact tag arrays |
| Discovered terms | ~100–300 | Only when new terms found |
| Extractable assets | ~50–150 | Up to 3 high-value passages |
| Suggested actors/networks | ~50–100 | Only when new entities found |
| Priority score | ~30 | Five integers |
| Metadata fields | ~50 | Date, scope, register, etc. |

**Context injection:** When algorithmic preprocessing data is available (NER, similarity, TF-IDF), it is injected as read-only context.

### 5.2 Research Summary — Design

The research summary replaces the former 5-section Zotero note. It is a **single prose paragraph of 80–150 words** that accompanies the document on the public archive page.

**Why prose, not sections:** On the archive page, the reader already sees structured tags, actor/network links, tactic chips, harm level, and entity connections as metadata. The summary should not duplicate this. Its job is to answer: *"What is this document doing and why does it matter?"*

**The summary must address (in natural prose, not labeled sections):**
1. What the document is and who produced it (1 sentence)
2. What rhetorical or political work it performs — the "so what" (1–2 sentences)
3. What makes it notable within the corpus — a specific passage, connection, escalation, or first use of a term (1–2 sentences)
4. What it connects to — a non-obvious link to another actor, network, or legal instrument (1 sentence, only if relevant)

**Token budget:** ~150–200 output tokens. Roughly 40–60% cheaper than the former 5-section note.

**For Zotero export:** A structured Zotero note is reconstructed at export time from tags + summary. The LLM does not generate Zotero structure — it is derivable from metadata.

### 5.3 AI Metadata

Every document record carries `ai_metadata` recording the full processing chain. This metadata is visible on the public archive page for methodological transparency.

```json
{
  "ai_metadata": {
    "primary_model": "string",
    "primary_provider": "anthropic",
    "validation_model": "string",
    "validation_provider": "openai",
    "prompt_version": "string",
    "ontology_version": "v3.0",
    "processing_date": "ISO datetime",
    "input_length_chars": "number",
    "truncated": "boolean",
    "agreement_status": "agreed | disagreed | not_yet_validated",
    "disagreements": ["string"],
    "resolution": "accepted_primary | accepted_validation | human_override",
    "human_review": {
      "reviewed_by": "researcher | intern",
      "reviewed_at": "ISO datetime",
      "changes_made": "boolean"
    },
    "algorithmic_preprocessing": {
      "tool": "unstructured | yt-dlp | whisper | manual | none",
      "ner_run": "boolean",
      "similarity_run": "boolean",
      "tfidf_run": "boolean"
    }
  }
}
```

**Displayed on public archive:** models used, agreement status, human review status, preprocessing tools, ontology version.

---

## 6. Dual-LLM Triangulation — Methodological Design

### 6.1 Why Two LLMs

Single-LLM classification has known failure modes: model-specific biases, hallucinated confidence, systematic blind spots. The dual-LLM approach provides triangulation, disagreement-as-signal, audit trail, bias detection, and vocabulary coverage (ChatGPT catches terms added since Claude's last prompt update).

### 6.2 The Flow

```
Document text
     |
     v
[Claude — primary ingestion]
  → tags, summary, terms, assets, priority
     |
     v
[HUMAN REVIEW #1]
  → approve/reject Claude tags
  → approve new terms → Lexicon grows
  → approve new actors → Registry grows
     |
     v
[Batch accumulates: 20-50 documents]
     |
     v
[ChatGPT — validation + supplementary]
  → validates Claude's tags
  → suggests ADDITIONAL tags Claude missed
  → extracts ADDITIONAL creative assets
  → flags disagreements
     |
     v
[Status: ready / needs_review / high_risk]
     |
     v
[HUMAN REVIEW #2]
  → resolves disagreements
  → reviews ChatGPT's additions
  → finalizes tags and assets
  → workflowStatus → verified
     |
     v
[Publication → Sanity → public archive]
```

### 6.3 Ontology Refinement Trigger

After each 20–50 doc batch: new terms → lexicon updated; new entities → registry updated; systematic patterns → ontology version increment. All changes logged.

### 6.4 ChatGPT Validation Prompt Design

Provisional prompt for validation, to be developed: `ChatGPT Validation Prompt.md`.

---

## 7. Human Review Layer

### 7.1 Key Principle

The researcher does NOT manually read every document. The system extracts; the human validates.

### 7.2 Human Review #1 — Post-Claude

Review Type/Format/Evidence → Country → Tactics → Terms → Scope/Flags/Landmarks → Date → Discovered terms (approve → Lexicon) → Suggested entities (approve → Registry) → Assets → Save.

### 7.3 Human Review #2 — Post-Validation

Review Claude vs. ChatGPT disagreements → ChatGPT's additional tag suggestions → ChatGPT's additional assets → Accept/reject/override → Advance to `verified`.

### 7.4 Publication

Only the researcher can set `workflowStatus: "published"`.

---

## 8. Token Economy and Payload Design

### 8.1 Cost Model

~$0.10–0.40 per document (Claude). ChatGPT on batches (lower amortized cost). Token efficiency directly affects sustainability across hundreds of documents.

### 8.2 Token Reduction Strategies

**Input:**
- Unstructured.io strips noise before LLM sees text
- Documents over 24,000 chars truncated (first 16k + last 6k)
- Boilerplate removal (cookie notices, navigation, footers)

**System prompt:**
- Vocabulary as compact lists, not verbose definitions
- Full definitions only for terms where context matters for classification
- Anthropic prompt caching where API supports it

**Output:**
- Prose summary: ~150–200 tokens (was ~250–500 for 5-section note)
- Compact tag arrays (strings, not objects)
- Discovered terms only when genuinely new
- Priority as five integers

**Payload split:** The LLM returns a compact classification payload (~500–1,500 tokens). The Vercel app wraps it in the full Sanity schema with IDs, timestamps, provenance, workflow status.

### 8.3 Compact Classification Payload (LLM output)

```json
{
  "type": "string",
  "format": "string",
  "evidence": ["string"],
  "country": ["string"],
  "tactic": ["string"],
  "actor": ["string"],
  "network": ["string"],
  "practice": ["string"],
  "term": ["string"],
  "harm": ["string"],
  "migration": ["string"],
  "function": ["string"],
  "scope": "string",
  "landmark": ["string"],
  "narrative_register": "string",
  "document_date": {"year": 0, "confidence": "string"},
  "summary": "string — 80-150 words",
  "priority": [0, 0, 0, 0, 0],
  "testimony_flag": false,
  "needs_review": false,
  "discovered_terms": [],
  "suggested_actors": [],
  "suggested_networks": [],
  "extractable_assets": []
}
```

The Vercel app expands this into the full document record (§14).

### 8.4 URL Harvesting — Zero LLM Cost

URL harvesting is deterministic (regex/DOM parsing). Zero tokens. If domain context is needed for classification, the app injects domain names only (~20–50 tokens), never full URL lists.

---

## 9. Experience Modules

Each module is standalone; all share the archive and lexicon.

### 9.1 JUST CHANGE™ *(active development)*

Critical RPG exposing conversion therapy through pop aesthetics. Single HTML file. `g.conv` (0→1) drives state. You always lose. Current: ZAP!, Cost of Amen, Overworld v6, rhythm game, Turn For Me. Target: 19 games. Aesthetic: Crayon-Prophet (pastels + televangelism gold, Space Grotesk).

### 9.2 SOGICE WebSearch Simulation

Simulated search engine funneling users toward SOGICE content. Pulls real quotes from archive.

### 9.3 The Retro SOGICE Library

1980s evangelical reading room with SOGICE books, pamphlets, documentaries.

### 9.4 Video Library / Documentary Archive

Ex-gay and gender ideology documentaries. Large files on Internet Archive.

### 9.5 Historical SOGICE Visualizer

Timeline driven by archive data and Landmark tags.

### 9.6 Trans Jesus Ministries Live

Speculative evangelical livestream. Counter-sermons, queer theology.

### 9.7 Courses and Ministries Tracker

SOGICE coaching programs, courses, ministry curricula. Feeds Network Visualizer.

### 9.8 PC Simulator

Three-act narrative (profile → targeting → no clean exit).

### 9.9 SOGICEfy and HOPE TV

Fake Spotify interface and broadcast segments.

---

## 10. WebXR and i-Doc Architecture

### 10.1 Design Principle

XR layer is a projection layer reading from the same archive. No separate content authoring.

### 10.2 Structure

Sequential documentary rooms · spatial archive as node network · permeable narrative/archive boundary · same URL for VR and desktop.

### 10.3 Stack

WebXR API · Three.js · JavaScript · Vercel hosting · Sanity data.

### 10.4 Shadow Play Aesthetic

Silhouettes behind frosted panels. Hidden lives under conversion therapy.

---

## 11. Ontology — Summary and Cross-Reference

Full ontology in `SOGICE_Ontology_v3.0.md`.

### 11.1 Seven Clusters

| # | Cluster | Core Question |
|---|---------|---------------|
| C1 | **SSA-Rhetoric** | Rename/reframe homosexuality as attraction or lifestyle? |
| C2 | **Pastoral-Coercion** | Frame conversion as spiritual care or healing? |
| C3 | **Pseudo-Science** | Misuse science, invent diagnoses, fabricate origin theories? |
| C4 | **Policy-Resistance** | Oppose bans using rights or freedom arguments? |
| C5 | **Anti-Trans/ROGD** | Target trans identity or gender-affirming care? |
| C6 | **Anti-Gender** | Frame LGBTQ+ rights as ideological takeover? |
| C7 | **Pro-Trans-SOGICE** | Oppose SOGICE for LGB while promoting it for trans? |

### 11.2 Two-Layer Model

**Layer A — Discourse:** clusters, tactics, terms, functions.
**Layer B — Practice-Regulatory:** practices, legal definitions, exclusion clauses.

### 11.3 Tag Instance

Every tag carries: tagType, tagValue, cluster, confidence, stance_profile, promotional_use, evidenceSnippets, rationale, reviewStatus, plus optional regulatory fields. `stance_profile` (promotional | critical_advocacy | legal_administrative | research_clinical) is primary; `cited_for_critique` retained as computed backwards-compatibility field.

### 11.4 Controlled Vocabulary

| Category | Cardinality | Notes |
|---|---|---|
| Type | Exactly one | 16 values |
| Format | Exactly one | 19 values |
| Evidence | **One or more** | 9 values — a document can be both Journalism and Testimony |
| Country | One or more | 26+ — organization's country |
| Tactic | One or more | 17 including PastoralCoercion-LegislativeLoophole, Operation-Gideon, Parental-Rights-Trans |
| Actor | Zero or more | 65+ |
| Network | Zero or more | 22+ |
| Practice | Zero or more | 14 including **Physical-Coercion**, **Verbal-Abuse-Humiliation** (ILGA-Europe aligned) |
| Term | Zero or more | 65+ (promotional use only) |
| Harm | Zero or more | 7 |
| Migration | Zero or more | 5 |
| Function | Zero or more | 12 |
| Scope | Exactly one | Core / Contextual / Reference |
| Landmark | Zero or more | 25+ |

---

## 12. Lexicon — Summary and Cross-Reference

Full lexicon in `SOGICE_Lexicon_v2.0.md`.

### 12.1 Purpose — SOGICE Wikipedia

The Lexicon functions as an interconnected knowledge base. Every entry links to related terms, source documents, actors, and legal instruments. The LLM ingestion builds this network: every processed document adds links, gradually constructing a navigable graph of SOGICE discourse.

### 12.2 Entry Structure

term · language_of_origin · languages_present · cluster · function · definition · first_documented_use · source_documents · context_quote · related_terms (with link type) · doctrinal_basis · attestation_tier (1/2/3) · multilingual_variants · review_status

### 12.3 Attestation Tiers

Tier-1: legal/policy text · Tier-2: NGO/academic sources · Tier-3: inferred (not valid as tagging target until confirmed)

---

## 13. Entity Model — Six Entity Types

Every entity exists once. Documents link to entities. Seed data in `Entity_Registry_v1.1.md`.

**Person:** id, name, former_names, role, affiliated_organizations, country, contested_figure + note, source_documents

**Organization:** id, name, former_names [{name, from_year, to_year}], type, country, founded/dissolved, parent, funding, description, source_documents

**Law / Policy:** id, name, country, year, status, applies_to, description, source_documents

**Event:** id, name, type, date, actors, description, historical_significance, source_documents

**LegalDefinition (new):** jurisdiction, instrument_type/name, year, term_used, target_dimensions, goal_verbs, harm_threshold, consent_override, exclusions [ExclusionClause._id], status

**ExclusionClause (new):** parent_legal_definition, excludes, text_excerpt, interpretation_risks, used_in_policy_arguments

---

## 14. JSON Schema — Document Record

The LLM produces the compact payload (§8.3). The Vercel app constructs the full record:

```json
{
  "_type": "document",
  "_id": "UUID",
  "workflowStatus": "unverified | in_progress | verified | published",

  "meta": {
    "source_url": "string",
    "archive_url": "string — auto-populated by Vercel Wayback check",
    "file_ref": "string — Sanity file asset reference",
    "ingested_at": "ISO datetime",
    "ingestion_batch": "string",
    "preprocessing_tool": "unstructured | yt-dlp | whisper | manual"
  },

  "provenance": {
    "original_url": "string",
    "accessed_via": "string",
    "wayback_url": "string",
    "html_snapshot_ref": "Sanity file asset ID",
    "chain_notes": "string"
  },

  "classification": {
    "type": "string",
    "format": "string",
    "evidence": ["string — one or more"],
    "scope": "string",
    "country": ["string"],
    "tactic": ["string"],
    "actor": ["string"],
    "network": ["string"],
    "practice": ["string"],
    "term": ["string"],
    "harm": ["string"],
    "migration": ["string"],
    "function": ["string"],
    "landmark": ["string"],
    "flags": ["string"]
  },

  "document_date": {
    "year": "number",
    "month": "number — optional",
    "day": "number — optional",
    "date_confidence": "exact | approximate | unknown"
  },

  "entities": {
    "actors_linked": ["entity _id"],
    "networks_linked": ["entity _id"],
    "laws_linked": ["entity _id"],
    "events_linked": ["entity _id"],
    "legal_definitions_linked": ["LegalDefinition _id"],
    "exclusion_clauses_linked": ["ExclusionClause _id"]
  },

  "relationships": [
    {
      "relationship_type": "translates | responds_to | cites | is_cited_by | co-produced_with | funded_by_same_source | part_of_series",
      "target_document_id": "string",
      "confidence": "confirmed | probable | speculative"
    }
  ],

  "content": {
    "title": "string",
    "summary": "string — 80-150 words prose",
    "summary_validation": "string — ChatGPT summary if available",
    "narrative_register": "string",
    "language_detected": "ISO 639-1",
    "word_count": "number"
  },

  "referenced_urls": [
    {
      "url": "string",
      "anchor_text": "string",
      "link_type": "internal | external | citation | unknown",
      "domain": "string",
      "resolved": "boolean",
      "archive_url": "string"
    }
  ],

  "social_media": {
    "account_name": "string",
    "follower_count_at_capture": "number",
    "hashtags": ["string"],
    "part_of_series": "boolean",
    "series_id": "string"
  },

  "priority_score": {
    "artistic": "1-5",
    "network": "1-5",
    "lexicon": "1-5",
    "testimony": "1-5",
    "historical": "1-5"
  },

  "extractable_assets": [
    {
      "asset_type": "prayer_script | testimony_excerpt | conversion_script | course_structure | statistical_claim | network_connection | terminology_coinage | visual_asset | legislative_quote | counter_sermon",
      "content": "string",
      "target_module": "JUST_CHANGE | WebSearch | Library | Trans_Jesus | Historical_Viz | XR_Room | Courses_Tracker | Video_Library | none",
      "extracted_by": "llm_primary | llm_validation | human"
    }
  ],

  "discovered_terms": [
    {
      "term": "string",
      "language": "ISO 639-1",
      "proposed_category": "string",
      "promotional_use": "boolean",
      "draft_definition": "string",
      "context_quote": "string",
      "suggests_new_tag": "string",
      "approved": "boolean"
    }
  ],

  "suggested_new_actors": [
    { "suggested_value": "string", "country": "string", "description": "string", "confidence": "high | medium", "approved": "boolean" }
  ],

  "suggested_new_networks": [
    { "suggested_value": "string", "description": "string", "confidence": "high | medium", "approved": "boolean" }
  ],

  "ai_metadata": {
    "primary_model": "string",
    "primary_provider": "string",
    "validation_model": "string",
    "validation_provider": "string",
    "prompt_version": "string",
    "ontology_version": "string",
    "processing_date": "ISO datetime",
    "input_length_chars": "number",
    "truncated": "boolean",
    "agreement_status": "agreed | disagreed | not_yet_validated",
    "disagreements": ["string"],
    "resolution": "accepted_primary | accepted_validation | human_override",
    "human_review": {
      "reviewed_by": "researcher | intern",
      "reviewed_at": "ISO datetime",
      "changes_made": "boolean"
    },
    "algorithmic_preprocessing": {
      "tool": "string",
      "ner_run": "boolean",
      "similarity_run": "boolean",
      "tfidf_run": "boolean"
    },
    "tag_provenance": [
      { "tag": "string", "layer": "algorithmic | llm_primary | llm_validation | human", "confidence": "0.0–1.0" }
    ]
  },

  "zotero": {
    "collection": "string",
    "exported_at": "ISO datetime"
  }
}
```

**Note:** `extracted_text` and `embedding_vector` stored in Sanity but excluded from this listing. `embedding_vector` excluded from public export and GROQ queries.

---

## 15. Testimony as a Separate Content Type

First-class objects: independently queryable, consent-controlled. Schema: source_document, testimony_type, consent_status, public_display (false by default), country_of_experience, denomination, practices_described, period, historical_period, extracted_text, narrative_module_flag, ai_metadata. Records with `consent_status: "unclear"` require researcher review. Contact page exists for removal requests.

---

## 16. Landmark Events and Named Scandals

Full vocabulary — see §16 in previous version (unchanged). Includes Operation Gideon Launch (2025), ILGA-Europe Intersections 2.0 (2026), PACE Resolution 2643 (2026), European Citizens' Initiative (2025), Matthew Grech Acquittal (2026), plus all existing landmarks.

---

## 17. Scope Logic

`Core` (European SOGICE) · `Contextual` (non-European, European relevance) · `Reference` (global/foundational). Upgrade allowed; downgrade requires logged reason.

---

## 18. URL Harvesting and Web Archiving

### 18.1 Automatic Archiving

On URL submission in Vercel app: query Wayback API → if exists, store URL → if not, trigger save → store HTML snapshot as Sanity asset.

### 18.2 URL Harvesting (Zero LLM Cost)

Deterministic regex/DOM parsing extracts outbound URLs. Stores domain, anchor text, link type. Domain context for LLM limited to ~20–50 tokens if needed.

---

## 19. Priority Scoring

Five axes (1–5): artistic, network, lexicon, testimony, historical. Claude assigns; human adjusts.

---

## 20. Storage, Backup, and Preservation

**Sanity** — live database + all binary files. **GitHub** — MD docs, folder structure, JSON backups. **Internet Archive** — large videos, documentaries.

---

## 21. Users and Permissions

| User | Read | Write | Publish | API Keys |
|---|---|---|---|---|
| Researcher | All | All | Yes | Holds keys |
| Intern | All | Tags, log, glossary | verified only | Via Vercel |
| Collaborator | All | Same as intern | No | Via Vercel |
| Public | Published only | No | No | No |

---

## 22. Non-Functional Requirements

Availability after PhD · 2–3 concurrent writers · no subscription for collaborators · Norwegian/EU hosting · three-tier visibility · multilingual sources · JSON/CSV export · FAIR compliance · AI transparency on public records · human-in-the-loop · dual-LLM audit trail · cost control (~$0.10–0.40/doc)

---

## 23. Intern Checklist

**Before tagging:** Term tags = promotional use only. Country = organization's country. Reference: TAGGING_GUIDE.md · Ontology v3.0 · Lexicon v2.0.

**Per document:** File → preprocess → Vercel app → Claude → review tags/terms/entities/assets → save.

**End of batch:** All fields assigned · no terms for criticism-only · all discoveries resolved · JSON to GitHub.

---

## 24. Phase Structure

| Phase | Focus | Deliverables |
|---|---|---|
| **0** | Ontology + tools | Ontology v3.0 · Lexicon v2.0 · Sanity schema · Vercel app · preprocessing scripts · pilot batch |
| **1** | Ingestion | Growing corpus via dual-LLM pipeline |
| **2** | Analysis | BERTopic · network graph · semantic map · ontology review |
| **3** | Public infrastructure | Archive + lexicon frontend (SOGICE Wikipedia) · network viz |
| **4** | Experience layer | JUST CHANGE™ · all modules · WebXR · i-Doc shell |

**June 2026:** JUST CHANGE™ WIP. **October 2026:** Full exhibition, public archive live.

---

## 25. Document Inventory

```
survivingsogice/
├── 00_infrastructure/
│   ├── SOGICE_Ontology_v3.0.md
│   ├── SOGICE_Lexicon_v2.0.md
│   └── Entity_Registry_v1.1.md
├── 01_project_docs/
│   ├── PRD_v3.0.md
│   └── DOCUMENT_MANIFEST.md
├── 02_working_tools/
│   ├── TAGGING_GUIDE.md
│   ├── SOGICE_LLM_Prompt.md
│   └── NotebookLM_Questionnaire.md
└── 03_data/
    ├── Term_More.md (raw source)
    └── exports/
```

---

## 26. Open Questions

| # | Question | Status |
|---|---|---|
| 5 | Norwegian org rebranding histories | Open — populate from corpus |
| 10 | Operation Gideon: "Oxygen-Gideon" not on iftcc.org/operation-gideon; requires corpus search | Open |
| 13 | France ExclusionClause (youth transition concerns) — legitimate or SOGICE-adjacent? | Open |
| 14 | JUST CHANGE™ i-Doc integration method | Open |
| 17 | ChatGPT validation prompt design | Open — Phase 0 deliverable |
| 18 | Testimony removal protocol | Contact page exists; formal protocol TBD |

**Resolved:** Q7 (Blanchard → Anti-Trans) · Q11 (France harm threshold → yes, model it) · Q12 (Physical-Coercion + Verbal-Abuse-Humiliation → added) · Q3 (domain → survivingsogice.eu) · Q15 (documentaries → Internet Archive) · Q16 (builder → Sérgio + Claude/Codex)

---

*Companion documents: SOGICE_Ontology_v3.0.md · SOGICE_Lexicon_v2.0.md · Entity_Registry_v1.1.md · TAGGING_GUIDE.md*
