"""
Sanity Content API client (httpx, REST mutations).

Reference: https://www.sanity.io/docs/http-mutations
Writes use the /mutate endpoint with a createOrReplace transaction.
"""
from __future__ import annotations
from datetime import datetime, timezone

import httpx

from ..config import Config
from ..models.document import DocumentPackage


def write_document(pkg: DocumentPackage, config: Config) -> str:
    """Write a sogiceDocument record to Sanity. Returns the Sanity document _id."""
    doc = _build_sanity_document(pkg)
    result = _mutate([{"createOrReplace": doc}], config)
    return result["results"][0]["id"]


def fetch_lexicon_terms(config: Config) -> list[dict]:
    """GROQ: all draft + validated lexicon entries with term, cluster, function."""
    query = (
        '*[_type == "lexiconEntry" && status in ["draft","validated"]]'
        '{ term, proposedCluster, function }'
    )
    url = (
        f"https://{config.sanity_project_id}.api.sanity.io"
        f"/v2024-01-01/data/query/{config.sanity_dataset}"
    )
    headers = {"Authorization": f"Bearer {config.sanity_write_token}"}
    r = httpx.get(url, params={"query": query}, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json().get("result", [])


def _build_sanity_document(pkg: DocumentPackage) -> dict:
    intake  = pkg.intake
    prep    = pkg.preprocess
    analysis = pkg.analysis
    now_iso  = datetime.now(timezone.utc).isoformat()

    return {
        "_type": "sogiceDocument",
        "_id":   f"doc-{intake.doc_id}",

        "workflowStatus": "unverified",
        "tier":           str(intake.tier),
        "tierAssignedBy": "auto",

        "meta": {
            "_type":              "object",
            "sourceUrl":          intake.source if intake.source_type == "url" else None,
            "archiveUrl":         intake.archive_url,
            "ingestedAt":         now_iso,
            "preprocessingTool":  prep.tool_used,
            "preprocessingQuality": prep.quality,
        },

        "classification": {
            "_type":            "object",
            "type":             analysis.type,
            "format":           analysis.format,
            "evidence":         analysis.evidence,
            "scope":            analysis.scope,
            "country":          analysis.country,
            "tactic":           analysis.tactic,
            "actor":            analysis.actor,
            "network":          analysis.network,
            "practice":         analysis.practice,
            "term":             analysis.term,
            "harm":             analysis.harm,
            "migration":        analysis.migration,
            "function":         analysis.function,
            "landmark":         analysis.landmark,
            "flags":            analysis.flags,
            "narrativeRegister": analysis.narrative_register,
        },

        "confidence": {
            "_type":        "object",
            "overallScore": analysis.confidence.overall_score,
            "status":       analysis.confidence.status,
            "reasons":      analysis.confidence.reasons,
            "signals": {
                "_type":           "object",
                "textQuality":     analysis.confidence.signals.text_quality,
                "languageClarity": analysis.confidence.signals.language_clarity,
                "contentStructure": analysis.confidence.signals.content_structure,
            },
        },

        "fieldConfidence": {
            "_type":   "object",
            "type":    analysis.field_confidence.type,
            "format":  analysis.field_confidence.format,
            "tactic":  analysis.field_confidence.tactic,
            "term":    analysis.field_confidence.term,
            "actor":   analysis.field_confidence.actor,
            "scope":   analysis.field_confidence.scope,
        },

        "documentDate": {
            "_type":          "object",
            "year":           analysis.document_date.year,
            "month":          analysis.document_date.month,
            "day":            analysis.document_date.day,
            "dateConfidence": analysis.document_date.confidence,
        },

        "content": {
            "_type":           "object",
            "summary":         analysis.summary,
            "languageDetected": prep.language_detected,
            "wordCount":       len(prep.text.split()),
        },

        "priorityScore": {
            "_type":     "object",
            "artistic":  analysis.priority.artistic,
            "network":   analysis.priority.network,
            "lexicon":   analysis.priority.lexicon,
            "testimony": analysis.priority.testimony,
            "historical": analysis.priority.historical,
        },

        "candidateTerms": [
            {
                "_type":           "object",
                "_key":            f"term-{i}",
                "term":            t.term,
                "language":        t.language,
                "proposedCategory": t.proposed_category,
                "promotionalUse":  t.promotional_use,
                "draftDefinition": t.draft_definition,
                "contextQuote":    t.context_quote,
                "approved":        False,
            }
            for i, t in enumerate(analysis.candidate_terms)
        ],

        "extractableAssets": [
            {
                "_type":       "object",
                "_key":        f"asset-{i}",
                "assetType":   a.asset_type,
                "content":     a.content,
                "targetModule": a.target_module,
                "extractedBy": a.extracted_by,
            }
            for i, a in enumerate(analysis.extractable_assets)
        ],

        "aiMetadata": {
            "_type":         "object",
            "primaryModel":  pkg.llm_used,
            "primaryProvider": "anthropic" if "claude" in pkg.llm_used else "local",
            "ontologyVersion": "v3.0",
            "processingDate": now_iso,
            "inputLengthChars": prep.char_count,
            "truncated":     prep.truncated,
            "agreementStatus": "not_validated",
            "resolution":    "not_applicable",
        },

        "testimonyFlag": analysis.testimony_flag,
        "needsReview":   analysis.needs_review,

        "validation": {
            "_type":  "object",
            "status": "not_validated",
        },
    }


def _mutate(mutations: list[dict], config: Config) -> dict:
    url = config.sanity_api_base
    headers = {
        "Authorization": f"Bearer {config.sanity_write_token}",
        "Content-Type":  "application/json",
    }
    response = httpx.post(url, json={"mutations": mutations}, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
