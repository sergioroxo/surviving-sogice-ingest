"""
Sanity Content API client (httpx, REST mutations).

Reference: https://www.sanity.io/docs/http-mutations
Writes use the /mutate endpoint with a createOrReplace transaction.
"""
from __future__ import annotations

import httpx

from ..config import Config
from ..models.document import DocumentPackage


def write_document(pkg: DocumentPackage, config: Config) -> str:
    """Write a document record to Sanity. Returns the Sanity document _id."""
    raise NotImplementedError


def fetch_lexicon_terms(config: Config) -> list[dict]:
    """GROQ query: *[_type == "lexiconEntry" && status in ["draft","validated"]]{ term, proposedCluster, function }"""
    raise NotImplementedError


def _build_sanity_document(pkg: DocumentPackage) -> dict:
    """Map DocumentPackage to the Sanity document schema (SANITY_SCHEMA_v1.0.md)."""
    raise NotImplementedError


def _mutate(mutations: list[dict], config: Config) -> dict:
    url = config.sanity_api_base
    headers = {
        "Authorization": f"Bearer {config.sanity_write_token}",
        "Content-Type": "application/json",
    }
    response = httpx.post(url, json={"mutations": mutations}, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
