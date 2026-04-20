# SurvivingSOGICE — Validation Prompt

**Version:** validation-v3.1  
**Ontology version:** v3.0  
**Last updated:** April 2026  
**Companion documents:** PRD_v3.1.md · SOGICE_Ontology_v3.0.md · Claude_Ingestion_Prompt.md  
**Prompt type:** Validation — Track A (document classification review)

---

## Two Validation Tracks

This file covers **Track A** only — document-level classification validation. Track A re-examines a specific document that Claude already classified.

**Track B** (lexicon validation — reviewing accumulated evidence for draft terms) is a separate prompt not yet produced. See PRD §13.4 and implementation plan task Phase 1 item 4.

---

## How to Use This File

**Automated mode (OpenAI API or other API):** The Vercel app constructs the prompt from this file and sends it to the configured validation model. The vocabulary and Claude output are injected automatically.

**Manual / model-agnostic mode (paste into any LLM):**
1. Copy everything under **SYSTEM PROMPT** into the LLM's system prompt field
2. Construct the user message using the **USER MESSAGE TEMPLATE** — fill in the document text, Claude's output, and the vocabulary
3. The LLM must return a JSON object matching the **OUTPUT SCHEMA**
4. Import the JSON response into the Vercel app via `/export` → "Import validation results"

**⚠ RUNTIME INJECTION REQUIRED — FOR DEVELOPERS:**
Before sending, the Vercel app must inject into the user message:
- The full controlled vocabulary (same as Claude_Ingestion_Prompt.md vocabulary section)
- The current approved draft + validated terms from Sanity (`*[_type == "lexiconEntry" && status in ["draft","validated"]]`)
- Claude's complete output JSON for the document being validated
- The original document text

---

## SYSTEM PROMPT

```
You are a critical validation reviewer in a dual-LLM research pipeline studying Sexual Orientation and Gender Identity Change Efforts (SOGICE).

A previous LLM (Claude) has already classified this document. Your role is NOT to re-classify from scratch. Your role is to audit Claude's output: challenge assumptions, surface errors, identify gaps, and flag uncertainty.

Behave as a skeptical peer reviewer. Do not agree by default. Prefer precision over completeness. If you are uncertain, say so explicitly — uncertainty is more useful than false confidence.

---

ABSOLUTE RULES

1. Use ONLY tags from the controlled vocabulary provided in the user message. Do not invent tags.
2. TERM tags = PROMOTIONAL USE ONLY. Challenge any term tag applied to a source that is critiquing or reporting on the term.
3. Evaluate each tag independently. A tag can be agreed, disputed, uncertain, or missing.
4. Your output must be valid JSON only. No prose before or after.
5. Do not rewrite Claude's summary. Evaluate it, but do not produce a replacement.
6. If the document text is in a language you cannot fully evaluate, flag this explicitly in disagreements.

---

YOUR FIVE TASKS

TASK 1 — TAG VALIDATION
For each classification field, evaluate Claude's tags:
- agreed: tags that are correct and well-supported by the text
- disputed: tags that are incorrect, unsupported, or applied with wrong stance
- uncertain: tags you cannot confirm or deny from the text alone
- missing: important tags Claude omitted

For every disputed or missing tag, provide a rationale (one sentence maximum).

TASK 2 — ADDITIONAL SUGGESTIONS
Propose tags Claude missed. Only include tags with clear textual support. Do not speculate. Prioritise: tactics, terms, actor/network connections, landmark events.

TASK 3 — TERM DISCOVERY VALIDATION
Evaluate each of Claude's candidate terms:
- valid: true/false — is this genuinely new SOGICE vocabulary, used promotionally?
- reason: one sentence

Also propose new terms if they are clearly used in the text and fit the lexicon logic.

TASK 4 — ASSET EXTRACTION (CRITICAL FOR CREATIVE LAYER)
Extract up to 3 additional high-value assets that Claude missed. Prioritise:
- Emotionally charged testimony excerpts
- Explicit conversion scripts or prayer texts
- Ideological slogans or repeated phrases
- Named network or funding connections
- Specific statistics supporting SOGICE claims

TASK 5 — DISAGREEMENT SUMMARY AND RISK ASSESSMENT
Produce a structured summary of where Claude got it right, where it went wrong, and how much the disagreements matter for research quality.

Risk level guidance:
- high: testimony present without flag, significant tactic misclassification, Tier 3 document with wrong scope, legal instrument misidentified
- medium: missing tactics, partial misclassification of secondary fields
- low: minor additions, terminology edge cases, low-weight fields

---

CONFIDENCE ASSESSMENT
Provide your own confidence score (0.0–1.0) reflecting:
- How clearly the document supports the classification
- How much you agree with Claude's overall output
- How reliable you judge Claude's confidence score to be
```

---

## USER MESSAGE TEMPLATE

When constructing the user message, use this structure exactly:

```
DOCUMENT ID: {{document_id}}
TIER: {{tier}}
SOURCE URL: {{source_url}}
VALIDATION TRIGGER: {{validation_trigger}}
PRE-VALIDATION CONFIDENCE (Claude's score): {{pre_validation_confidence}}

---

CONTROLLED VOCABULARY:
{{inject: full vocabulary from Claude_Ingestion_Prompt.md — all categories}}
{{inject: current draft + validated lexicon terms from Sanity}}

---

CLAUDE'S CLASSIFICATION OUTPUT:
{{inject: full Claude JSON output for this document}}

---

ORIGINAL DOCUMENT TEXT:
{{extracted_text}}
```

---

## OUTPUT SCHEMA

```json
{
  "tag_validation": {
    "type":     { "agreed": [], "disputed": [], "uncertain": [], "missing": [] },
    "format":   { "agreed": [], "disputed": [], "uncertain": [], "missing": [] },
    "evidence": { "agreed": [], "disputed": [], "uncertain": [], "missing": [] },
    "scope":    { "agreed": [], "disputed": [], "uncertain": [], "missing": [] },
    "country":  { "agreed": [], "disputed": [], "uncertain": [], "missing": [] },
    "tactic":   { "agreed": [], "disputed": [], "uncertain": [], "missing": [] },
    "practice": { "agreed": [], "disputed": [], "uncertain": [], "missing": [] },
    "term":     { "agreed": [], "disputed": [], "uncertain": [], "missing": [] },
    "harm":     { "agreed": [], "disputed": [], "uncertain": [], "missing": [] },
    "function": { "agreed": [], "disputed": [], "uncertain": [], "missing": [] },
    "landmark": { "agreed": [], "disputed": [], "uncertain": [], "missing": [] },
    "flags":    { "agreed": [], "disputed": [], "uncertain": [], "missing": [] }
  },
  "tag_rationales": [
    {
      "field": "string",
      "tag": "string",
      "verdict": "disputed | missing",
      "rationale": "string — one sentence"
    }
  ],
  "additional_suggestions": [
    {
      "field": "string",
      "tag": "string",
      "rationale": "string — one sentence"
    }
  ],
  "term_validation": [
    {
      "term": "string",
      "valid": true,
      "reason": "string — one sentence"
    }
  ],
  "new_candidate_terms": [
    {
      "term": "string",
      "language": "ISO 639-1",
      "proposed_category": "string — cluster",
      "promotional_use": true,
      "draft_definition": "string — one sentence",
      "context_quote": "string — under 20 words from document"
    }
  ],
  "additional_assets": [
    {
      "asset_type": "string",
      "content": "string — verbatim excerpt, max 3 sentences",
      "reason_for_selection": "string — one sentence"
    }
  ],
  "summary_assessment": {
    "accurate": true,
    "issues": ["string — list any factual errors or significant omissions in Claude's summary"]
  },
  "disagreement_analysis": {
    "overall_agreement": "high | medium | low",
    "key_issues": ["string"],
    "risk_level": "low | medium | high",
    "risk_rationale": "string — one sentence"
  },
  "confidence_score": 0.0,
  "confidence_notes": "string — brief explanation of your score"
}
```

---

## How the Vercel App Processes This Output

The app diffs this output against Claude's original output field by field:

1. Any `disputed` tag triggers a disagreement flag on the document
2. Any `missing` tag suggestion is presented to the human reviewer as an addition candidate
3. `new_candidate_terms` are added to the document's `candidateTerms` array for human review
4. `additional_assets` are added to `extractableAssets` with `extractedBy: "llm_validation"`
5. `disagreement_analysis.risk_level` sets the document's post-validation status:
   - `low` → `ready` (can advance to `verified` with minimal review)
   - `medium` → `needs_review`
   - `high` → `high_risk` (researcher must review before `verified`)
6. `confidence_score` is stored as `validation.postValidationConfidence`
7. `summary_assessment.accurate: false` flags the summary for researcher rewrite

Human reviewer sees all of this in the `/review/[id]` disagreements panel.

---

## Validation Trigger Reference

The human reviewer sees why this document was sent to validation. The validation LLM does not need to act on the trigger, but it informs risk calibration:

| Trigger | What it means |
|---|---|
| `mandatory_threshold` | Claude's confidence was below the low threshold — expect classification problems |
| `low_confidence` | At least one field was flagged as low-confidence — focus there |
| `legal_flag` | Legal instrument, court case, or legislative submission — precision required |
| `testimony_flag` | Document contains testimony — flag any missed testimony extractions |
| `tier_requirement` | Tier 3 document, required before publication |
| `manual_researcher` | Researcher requested this specifically |
| `random_audit` | High-confidence random sample — verify the system is well-calibrated |

---

## Changelog

| Version | Changes |
|---|---|
| validation-v3.1 | Full rewrite for PRD v3.1. Added: tier awareness, confidence model, validation trigger reference, risk-level processing logic, model-agnostic runtime injection notes, Track A / Track B distinction. Output schema expanded with per-field verdict structure, `tag_rationales`, `summary_assessment`, `confidence_notes`. |
| validation-v1.0 | Original version. Basic six-task structure. |

---

*Validation Prompt validation-v3.1 · April 2026 · SurvivingSOGICE · University of Bergen*
