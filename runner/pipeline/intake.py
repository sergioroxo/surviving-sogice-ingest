"""
Stage 1 — Source intake.

Detects source type (URL / PDF / video / SRT / EPUB), generates a stable doc_id,
checks the Wayback Machine for URL sources, assigns tier and batch,
creates the local corpus directory.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import uuid

from ..config import Config
from ..models.document import IntakeResult


def run(
    source: str,
    tier: Optional[int],
    batch: Optional[str],
    config: Config,
) -> IntakeResult:
    raise NotImplementedError


def _detect_source_type(source: str):
    raise NotImplementedError


def _generate_doc_id() -> str:
    return str(uuid.uuid4())[:8]


def _auto_assign_tier(source_type: str, declared_type: str) -> int:
    raise NotImplementedError


def _archive_url(url: str, config: Config) -> Optional[str]:
    """Check Wayback Machine for existing snapshot; save if none found.
    Returns archive URL or None on failure (never blocks intake on failure)."""
    raise NotImplementedError


def _create_local_dir(doc_id: str, config: Config) -> Path:
    doc_dir = config.corpus_dir / doc_id
    doc_dir.mkdir(parents=True, exist_ok=True)
    return doc_dir
