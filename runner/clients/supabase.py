"""
Supabase client wrapper.

Handles upserts to the document_embeddings table.
The vector column dimension must match qwen3-embedding:4b output (Q22).
"""
from __future__ import annotations

from ..config import Config
from ..models.document import AnalysisResult


def _client(config: Config):
    from supabase import create_client
    return create_client(config.supabase_url, config.supabase_service_key)


def upsert_embedding(
    doc_id: str,
    vector: list[float],
    analysis: AnalysisResult,
    config: Config,
) -> None:
    """Insert or update a row in document_embeddings."""
    raise NotImplementedError


def insert_null_row(doc_id: str, config: Config) -> None:
    """Create a null-vector placeholder row at intake time (Phase 0-B requirement)."""
    raise NotImplementedError
