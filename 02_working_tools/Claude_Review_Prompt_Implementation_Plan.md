# Prompt for Claude: Implementation Plan Verification & Enhancement

**Purpose:** 
Copy and paste this entire document into Claude. It contains an analysis of the gaps between the current `IMPLEMENTATION_PLAN_v1.0.md`, the PRD (`PRD_v3.1.md`), and the infrastructure schemas (`SANITY_SCHEMA_v1.0.md`, `SOGICE_Ontology_v3.0.md`).

---

## **Prompt to submit to Claude:**

**Role:** You are an expert technical project manager and systems architect. You are reviewing the core Implementation Plan for the "SurvivingSOGICE" project. 

**Context:** The project uses Sanity.io (CMS), Supabase (pgvector for semantic search), Next.js (App Router), and Anthropic's API (Claude) to ingest, classify, and analyze documents related to SOGICE (Sexual Orientation and Gender Identity Change Efforts).

**The Problem:** We recently cross-referenced our `IMPLEMENTATION_PLAN_v1.0.md` against our `PRD_v3.1.md` and `SANITY_SCHEMA_v1.0.md`. We found several discrepancies, missing steps, and areas where the Implementation Plan does not fully cover the PRD or Schema requirements.

Here is the list of identified gaps:

### 1. Critical Path & Sequencing Issues
*   **Entity Registry seeding timing unclear:** Task 0-A-4 mentions seeding from the Entity Registry but doesn't specify when relative to other Phase 0 tasks. This must be a prerequisite before 0-D/0-E.
*   **Preprocessing prerequisite not explicit:** Task 0-G (preprocessing scripts) should be a hard blocker before 0-E (Claude ingestion), but the dependency diagram doesn't enforce this.
*   **Validation prompts finalization incomplete:** Tasks 0-I and 0-J lack success criteria and sign-off ownership. Who tests? What constitutes "tested and locked"?

### 2. Schema-to-Pipeline Coverage Gaps
*   **Testimony workflow underspecified:** The Sanity schema defines a full `testimony` type with consent and tier logic. Task 0-F-9 mentions a "testimony flag alert" but has no dedicated extraction, consent review, or moderation workflow task.
*   **Zotero export undefined:** The Schema includes a `zotero` field and the PRD mentions Zotero export, but Phase 0 has no task defining the Zotero schema or export format. This is reduntant for the new project, probably was an old element, but we can add Zotero API if it makes sense.
*   **No Phase 0 task for public archive/lexicon frontend design:** The plan jumps from ingestion (Phase 0) to publication (Phase 3) with no frontend prototyping phase.
*   **ExclusionClause and LegalDefinition schemas missing:** `SANITY_SCHEMA` references these as first-class entity types, but the Implementation Plan never mentions creating or seeding them.

### 3. Infrastructure & Ontology Integration Gaps
*   **Ontology injection not detailed:** The plan mentions injecting the controlled vocabulary, but fails to specify *which* ontology sections (clusters, tactics, practices, legal definitions) get inserted where and when in the system prompt.
*   **Lexicon/Ontology version alignment not tracked:** How do version updates to the Ontology propagate to running prompts? When do we re-test ingestion with a new ontology?

### 4. Validation System Gaps
*   **Confidence threshold calibration starting points:** Phase 0.5 says thresholds "will be calibrated" but provides no initial baseline values to test (e.g., 0.85 high, 0.70 medium).
*   **Validation trigger logic incomplete:** PRD lists 7 triggers (mandatory_threshold, low_confidence, legal_flag, testimony_flag, etc.). Task 0-I doesn't specify which are implemented in Phase 0 vs Phase 0.5 vs Phase 1.
*   **Track A vs. Track B separation:** The plan mentions both document classification validation and lexicon evidence validation but doesn't explicitly sequence them.

### 5. Multilingual & Error Handling Coverage
*   **Multilingual testing not mandated in Pilot:** PRD specifies 5 languages (Norwegian, Portuguese, Italian, French, German). Phase 0.5 pilot only mentions "at least 3 languages" and doesn't explicitly mandate testing Claude's output across them. The project envolves all of Europe, not limited to 5 or 3.
*   **API / Wayback Machine failure handling underspecified:** What is the retry logic for Anthropic API rate limits? What is the fallback if the Wayback Machine API is down? How is the image stored?

### 6. Intern & Consent Workflows
*   **Intern access verification missing:** There is no explicit Phase 0 or 0.5 task to verify the intern workflow end-to-end (testing that they can write tags but have no publish rights and no API key exposure). The intern will probably loose access to facilitate complexity.
*   **Consent review workflow not standalone:** Providing testimony consent is critical, but there is no dedicated workflow defined for it.

---

### **Your Task (Claude):**

Based on the gaps listed above, please:
1. **Verify these findings:** Do they accurately reflect standard architectural and project management best practices for a system of this complexity?
2. **Draft the necessary additions:** Write out the specific new tasks, sub-tasks, and dependency updates that need to be injected into `IMPLEMENTATION_PLAN_v1.0.md`. Provide them as ready-to-copy Markdown blocks.
3. **Propose a revised Dependency Map:** Rewrite the dependency tree at the bottom of the Implementation Plan to properly reflect Preprocessing blockers, Entity Registry seeding, and the prompt lock dates.
4. **Resolution for Q22:** Propose exactly *when* the Q22 decision (Embedding model: OpenAI vs. local `mpnet`) should be locked to prevent Phase 2 delays.