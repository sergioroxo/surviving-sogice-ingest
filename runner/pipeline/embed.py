"""
Stage 3a — Embedding generation.

Uses qwen3-embedding:4b via Ollama by default.
Writes embedding.json to the local corpus directory.

IMPORTANT: Run `python -m runner embed-test` before Phase 0-B to verify the
output dimension of qwen3-embedding:4b. Record the result in CLAUDE.md (Q22).
The Supabase vector column dimension must match exactly.
"""
from __future__ import annotations
import json
from pathlib import Path

from ..config import Config


def run(text: str, config: Config) -> list[float]:
    """Generate embedding vector for the given text. Returns list of floats."""
    raise NotImplementedError


def test_dimension(config: Config) -> int:
    """Embed a short test string and return the vector dimension.
    Called by `runner embed-test` to resolve Q22."""
    vector = run("SurvivingSOGICE embedding dimension test.", config)
    return len(vector)


def save(doc_id: str, vector: list[float], config: Config) -> None:
    doc_dir = config.corpus_dir / doc_id
    payload = {
        "doc_id": doc_id,
        "model": config.embedding_model,
        "dimension": len(vector),
        "vector": vector,
    }
    (doc_dir / "embedding.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
