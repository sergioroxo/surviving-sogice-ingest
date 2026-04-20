# PROJECT VALIDITY & ARCHITECTURAL SUGGESTIONS v1.0

**Based on:** Cross-review of PRD v3.1, Implementation Plan v1.0, Sanity Schema v1.0, and foundational infrastructure docs by specialized AI agents.
**Review focus:** Technical architecture, scale (pan-European context), social/educational impact, safety, and operational complexity.

---

## Executive Summary

The SurvivingSOGICE platform is architecturally ambitious and sets a strong foundation for managing sensitive data. However, our specialized review has identified several critical flaws that threaten its ability to scale across Europe, protect its users, and function reliably during data ingestion. 

The most pressing issues fall into three categories:
1. **Technical Scalability:** The vector embedding schema is hardcoded to a model that cannot support 15+ European languages, breaking the promise of pan-European analysis.
2. **Data Ingestion Resiliency:** The fallback mechanisms for archiving (Wayback Machine) and processing (missing Image OCR) are brittle and incomplete, risking massive data loss for visual or dynamic content.
3. **Social/Educational Safety:** The system lacks vital protective UX layers (redaction workflows, plain-English definitions, and trigger warnings) necessary for a public-facing social impact project dealing with traumatic material. Access control is also unnecessarily complex.

---

## 1. Technical Architecture & Scale Flaws

### 1.1 Multilingual Vector Embedding Scaling (CRITICAL)
*   **The Flaw:** The Supabase schema is hardcoded to `content_embedding vector(1536)`. This locks the project into models like OpenAI's `text-embedding-3-small`. However, Europe has 50+ languages. To support a true pan-European tracking system (Norwegian, Portuguese, Italian, French, German, Spanish, Slavic languages, etc.), you *must* use a robust multilingual model (like `paraphrase-multilingual-mpnet-base-v2`, which is 768-dimensional). The current schema makes swapping models impossible without a complete database migration and re-embedding of all documents.
*   **Recommendation:**
    *   Do not hardcode `vector(1536)` in Phase 0. 
    *   **Decision Q22 MUST be resolved before Phase 0-B.** If you want to cover all of Europe affordably and privately, choose a local multilingual model (e.g., 768-dim) now, or use a schema-less vector database like Weaviate/Milvus.
    *   Define semantic alignment rules: Document how cross-lingual queries will be judged (e.g., does Spanish "Conversión" map to English "Conversion therapy" in the vector space?).

### 1.2 Image Storage, OCR, and Wayback Fallbacks (CRITICAL)
*   **The Flaw:** Documents contain screenshots, logos, and diagrams (often containing critical lexicon terms). The current design stores images as Sanity file assets but has **no OCR pipeline**. Furthermore, the fallback for the Wayback Machine ("direct HTML download") is brittle, fails on JavaScript-heavy sites, and does not capture live context if the site goes down entirely.
*   **Recommendation:**
    *   **Add an OCR Pipeline (Phase 0-G):** Integrate `Tesseract` (handles European languages natively) or `PaddleOCR` to extract text from all identified images. Store this as `extracted_from_image` to feed the Lexicon.
    *   **3-Tier Archival Fallback:** 
        1. Query Wayback API.
        2. If missing, POST to save to Wayback and poll.
        3. If failed 3x, use Playwright/Puppeteer to render a PDF/Screenshot of the live site (this handles JS and CSS properly), upload it to Sanity, and flag `archival_failure: true` for the Wayback link.
    *   Use a CDN (Cloudinary/Imgix) for serving images to reduce bandwidth costs when the public archive goes live.

### 1.3 Access Control & Intern Roles (HIGH)
*   **The Flaw:** The user noted, *"The intern will probably loose access to facilitate complexity."* Currently, the system has 3 roles (Researcher, Intern, Collaborator) but only 1 real constraint: *Who can publish?* Managing these roles via Vercel middleware is fragile. Furthermore, holding API keys in local environments is a severe security risk.
*   **Recommendation:**
    *   **Simplify to Two Roles:** Editor (Researcher) and Reviewer (temporary/intern). 
    *   Enforce the "Publish" gate strictly at the **Sanity schema layer**, not just Vercel. Attempting to save a document with `published` status should return a 403 for Reviewers.
    *   **Implement a Service Account for API calls:** Researchers should not hold OpenAI/Anthropic keys locally. Keys should live exclusively in Vercel environment variables, accessed via a backend `/api/ingest` route, with strict rate limiting to protect the budget.

---

## 2. Social, Educational, and Ethical Impact Flaws

### 2.1 Consent Workflows and Testimony Redaction (CRITICAL)
*   **The Flaw:** Testimony is rightly separated as a core object, but the consent workflow is highly paternalistic (researcher-assumed consent). Current logic is binary: `publicDisplay: true` (shows everything) or `false` (shows nothing).

### 2.2 Public UX: Definition Accessibility & Stance (HIGH)
*   **The Flaw:** The SOGICE Wikipedia is meant to be educational, but academic lexicon definitions ("Pseudo-Diagnostic Rhetoric...") are inaccessible to the general public (e.g., high school students or victims seeking answers). Additionally, when a user views a term, they see 50 evidence documents but won't immediately know if those documents are *promoting* or *condemning* the practice.
*   **Recommendation:**
    *   **Accessible Definitions:** Add an `accessibleDefinition` field (max 1-2 plain-English sentences) to the `lexiconEntry` schema. Show this first on the frontend, with a "Read detailed academic definition" toggle for the `draftDefinition`.
    *   **Stance Color-Coding:** The schema already tracks `stanceProfile`. The frontend MUST color-code evidence dossiers to provide immediate context (e.g., 🔴 Promotional/Pro-SOGICE vs. 🟢 Critical Advocacy).


### 2.4 Integration of "JUST CHANGE™" Games (MEDIUM)
*   **The Flaw:** JUST CHANGE™ is structurally isolated. While the games act as an "experience layer," Phase 4 lacks explicit paths for how the Sanity data actually feeds the games to multiply the social impact.
*   **Recommendation:**
    *   Define the GROQ queries in Phase 0/1 that will feed the "archive-connected game" (e.g., fetching 10 random Tier 3 `testimony` redactions to serve as narrative text in the game's "Overworld v6").
    *   Ensure the game's end-state or failure-state provides the player a direct link back to the SOGICE Wikipedia to learn *why* the mechanics function the way they do in reality.