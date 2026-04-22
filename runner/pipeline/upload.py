"""
Stage 5 — Upload and export.

After researcher approval at Checkpoint 4:
  1. Save full document package locally (always happens first)
  2. Write Sanity document record (workflowStatus: unverified)
  3. Insert/update Supabase document_embeddings row
  4. Write sanity_record.json locally

Sanity writes use httpx via clients/sanity.py.
Supabase writes use supabase-py via clients/supabase.py.
"""
from __future__ import annotations
import json
from pathlib import Path

from rich.console import Console

from ..config import Config
from ..models.document import AnalysisResult, DocumentPackage, IntakeResult, PreprocessResult
from ..clients import sanity as sanity_client
from ..clients import supabase as supabase_client

console = Console()


def run(
    intake: IntakeResult,
    preprocess: PreprocessResult,
    embedding: list[float],
    analysis: AnalysisResult,
    config: Config,
) -> None:
    pkg = DocumentPackage(
        intake=intake,
        preprocess=preprocess,
        analysis=analysis,
        embedding=embedding,
        embedding_model=config.embedding_model,
        llm_used="unknown",
        local_dir=config.corpus_dir / intake.doc_id,
    )
    local_path = save_locally(intake, preprocess, embedding, analysis, config)
    sanity_id = sanity_client.write_document(pkg, config)
    supabase_client.upsert_embedding(intake.doc_id, embedding, analysis, config)
    console.print(f"[green]Uploaded[/green] → Sanity: {sanity_id}")


def save_locally(
    intake: IntakeResult,
    preprocess: PreprocessResult,
    embedding: list[float],
    analysis: AnalysisResult,
    config: Config,
) -> Path:
    """Write all artifacts to ~/survivingsogice/corpus/{doc_id}/. Always called before upload."""
    doc_dir = config.corpus_dir / intake.doc_id
    doc_dir.mkdir(parents=True, exist_ok=True)

    (doc_dir / "analysis.json").write_text(
        analysis.model_dump_json(indent=2), encoding="utf-8"
    )
    (doc_dir / "embedding.json").write_text(
        json.dumps({"model": config.embedding_model, "dimension": len(embedding), "vector": embedding}, indent=2),
        encoding="utf-8",
    )
    _write_audit_event(doc_dir, "saved_locally")
    return doc_dir


def list_pending(config: Config) -> None:
    """Print all local documents that have no sanity_record.json (not yet uploaded)."""
    raise NotImplementedError


def upload_saved(doc_id: str, config: Config) -> None:
    """Load a locally saved document and upload it to Sanity + Supabase."""
    raise NotImplementedError


def export_batch(batch_id: str, config: Config) -> None:
    """Export all documents in a batch as JSON to exports/{batch_id}/."""
    raise NotImplementedError


def _write_audit_event(doc_dir: Path, event: str) -> None:
    from datetime import datetime, timezone
    audit_path = doc_dir / "audit.log"
    ts = datetime.now(timezone.utc).isoformat()
    with audit_path.open("a", encoding="utf-8") as f:
        f.write(f"{ts} {event}\n")
