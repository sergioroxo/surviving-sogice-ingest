"""
Stage 3a — Embedding generation.

Uses qwen3-embedding:4b via Ollama by default (direct REST call, no library
version dependency). Writes embedding.json to the local corpus directory.

IMPORTANT: Run `python -m runner embed-test` before Phase 0-B to verify the
output dimension of qwen3-embedding:4b. Record the result in CLAUDE.md (Q22).
The Supabase vector column dimension must match exactly.
"""
from __future__ import annotations
import json
from pathlib import Path

import httpx

from ..config import Config

_TIMEOUT = 120  # seconds — embedding a long document can be slow on first run


def run(text: str, config: Config) -> list[float]:
    """Generate embedding vector for the given text via Ollama REST API."""
    response = httpx.post(
        f"{config.ollama_base_url}/api/embeddings",
        json={"model": config.embedding_model, "prompt": text},
        timeout=_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["embedding"]


def test_dimension(ollama_base_url: str, model: str) -> int:
    """Embed a short test string and return the vector dimension.
    Called by `runner embed-test` to resolve Q22.
    Does not require API keys — only needs Ollama running locally."""
    response = httpx.post(
        f"{ollama_base_url}/api/embeddings",
        json={"model": model, "prompt": "SurvivingSOGICE embedding dimension test."},
        timeout=_TIMEOUT,
    )
    response.raise_for_status()
    return len(response.json()["embedding"])


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
