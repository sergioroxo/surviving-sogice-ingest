"""
SurvivingSOGICE ingestion runner.

Usage:
  python -m runner ingest <url-or-file>
  python -m runner ingest document.pdf --tier 2 --batch batch-07
  python -m runner ingest recording.mp4 --llm local
  python -m runner ingest document.pdf --llm both
  python -m runner status
  python -m runner upload <doc_id>
  python -m runner export batch-07
  python -m runner embed-test
"""
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel

from .config import load_config
from .pipeline import intake, preprocess, embed, analyze, review, upload

app = typer.Typer(name="runner", add_completion=False)
console = Console()


@app.command()
def ingest(
    source: str = typer.Argument(..., help="URL, PDF path, video file, SRT, or EPUB"),
    llm: str = typer.Option("claude", help="LLM: claude | local | both | prefer-local | prefer-claude"),
    tier: Optional[int] = typer.Option(None, help="Override auto-assigned tier (1|2|3)"),
    batch: Optional[str] = typer.Option(None, help="Assign to existing batch ID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Auto-approve all checkpoints (no interactive prompts)"),
):
    """Full ingestion pipeline: intake → preprocess → embed → classify → review → upload."""
    config = load_config()

    # Stage 1 — Intake
    intake_result = intake.run(source, tier=tier, batch=batch, config=config)
    if not yes and not review.checkpoint_intake(intake_result):
        raise typer.Exit()

    # Stage 2 — Preprocessing
    preprocess_result = preprocess.run(intake_result, config=config)
    if not yes and not review.checkpoint_preprocess(preprocess_result):
        raise typer.Exit()

    # Stage 3 — Embedding + Analysis
    embedding_vector = embed.run(preprocess_result.text, config=config)
    analysis_result = analyze.run(preprocess_result, llm=llm, config=config)

    # Stage 4 — Analysis review (Checkpoint 3)
    final_analysis = review.checkpoint_analysis(
        analysis_result, doc_id=intake_result.doc_id, yes=yes
    )
    if final_analysis is None:
        raise typer.Exit()

    # Stage 5 — Upload confirmation (Checkpoint 4)
    confirmed = yes or review.checkpoint_upload(intake_result.doc_id, final_analysis)
    if confirmed:
        upload.run(intake_result, preprocess_result, embedding_vector, final_analysis, config=config)
    else:
        saved_path = upload.save_locally(intake_result, preprocess_result, embedding_vector, final_analysis, config=config)
        console.print(Panel(
            f"Saved locally at [bold]{saved_path}[/bold]\n\n"
            f"Upload later with: [bold]python -m runner upload {intake_result.doc_id}[/bold]",
            title="Saved locally",
        ))


@app.command()
def status():
    """List documents saved locally that have not yet been uploaded to Sanity."""
    config = load_config()
    upload.list_pending(config)


@app.command()
def upload_doc(
    doc_id: str = typer.Argument(..., help="doc_id of a locally saved document"),
):
    """Upload a locally saved document to Sanity and Supabase."""
    config = load_config()
    upload.upload_saved(doc_id, config)


@app.command(name="export")
def export_batch(
    batch_id: str = typer.Argument(..., help="Batch ID to export"),
):
    """Export all documents in a batch as JSON to exports/{batch_id}/."""
    config = load_config()
    upload.export_batch(batch_id, config)


@app.command(name="embed-test")
def embed_test():
    """Run a test embedding and print the vector dimension. Do this before Phase 0-B."""
    config = load_config()
    dim = embed.test_dimension(config)
    console.print(Panel(
        f"[bold green]qwen3-embedding:4b output dimension: {dim}d[/bold green]\n\n"
        f"Record this in CLAUDE.md under Open Questions (Q22).\n"
        f"Use [bold]vector({dim})[/bold] when creating the Supabase table.",
        title="Embedding Dimension",
    ))


if __name__ == "__main__":
    app()
