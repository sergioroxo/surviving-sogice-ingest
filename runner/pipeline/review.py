"""
Human-in-the-loop checkpoints.

All four checkpoints use Rich panels for display and typer.confirm / Prompt
for researcher input. Each returns True to proceed, False to abort/defer.
"""
from __future__ import annotations
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import typer

from ..models.document import AnalysisResult, IntakeResult, PreprocessResult

console = Console()


def checkpoint_intake(intake: IntakeResult) -> bool:
    """Checkpoint 1 — display source metadata, ask researcher to proceed."""
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("Source:", intake.source)
    table.add_row("Type:", intake.source_type)
    table.add_row("Tier:", str(intake.tier))
    table.add_row("Batch:", intake.batch_id)
    table.add_row("Doc ID:", intake.doc_id)
    if intake.language:
        table.add_row("Language:", intake.language)
    if intake.archive_url:
        table.add_row("Archive URL:", intake.archive_url)

    console.print(Panel(table, title="[bold]SOURCE INTAKE[/bold]"))
    return typer.confirm("Proceed with preprocessing?", default=True)


def checkpoint_preprocess(result: PreprocessResult) -> bool:
    """Checkpoint 2 — show preprocessing summary, let researcher inspect extracted.md."""
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("Tool:", result.tool_used)
    table.add_row("Quality:", _quality_badge(result.quality))
    table.add_row("Characters:", str(result.char_count))
    table.add_row("Truncated:", "yes" if result.truncated else "no")
    if result.language_detected:
        table.add_row("Language detected:", result.language_detected)
    if result.ocr_images:
        table.add_row("OCR images:", str(len(result.ocr_images)))

    console.print(Panel(table, title="[bold]PREPROCESSING RESULT[/bold]"))

    action = typer.prompt(
        "Action",
        default="proceed",
        show_choices=True,
        type=typer.Choice(["proceed", "edit", "abort"]),
    )
    if action == "abort":
        return False
    if action == "edit":
        _open_in_editor(result)
        return checkpoint_preprocess(result)
    return True


def checkpoint_analysis(
    result: AnalysisResult,
    doc_id: str,
    yes: bool = False,
) -> Optional[AnalysisResult]:
    """Checkpoint 3 — display classification fields, return (possibly edited) result.
    Returns None if researcher aborts."""
    raise NotImplementedError


def checkpoint_upload(doc_id: str, result: AnalysisResult) -> bool:
    """Checkpoint 4 — confirm Sanity + Supabase upload."""
    candidate_count = len(result.candidate_terms)
    actor_count = len(result.suggested_actors)

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("Doc ID:", doc_id)
    table.add_row("Type:", result.type)
    table.add_row("Scope:", result.scope)
    table.add_row("Confidence:", f"{result.confidence.overall_score:.2f} ({result.confidence.status})")
    table.add_row("Candidate terms:", str(candidate_count))
    table.add_row("Suggested actors:", str(actor_count))

    will_do = Text()
    will_do.append("• Write to Sanity (workflowStatus: unverified)\n")
    will_do.append("• Sync embedding to Supabase\n")
    will_do.append("• Save local backup\n")

    console.print(Panel(table, title="[bold]UPLOAD CONFIRMATION[/bold]"))
    console.print(will_do)

    action = typer.prompt(
        "Action",
        default="upload",
        type=typer.Choice(["upload", "local-only", "review-again", "abort"]),
    )
    return action == "upload"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _quality_badge(quality: str) -> Text:
    colors = {"high": "green", "medium": "yellow", "low": "red", "blocked": "bold red"}
    return Text(quality, style=colors.get(quality, "white"))


def _open_in_editor(result: PreprocessResult) -> None:
    import subprocess, os
    if result.markdown:
        path = _markdown_path(result)
        editor = os.environ.get("EDITOR", "nano")
        subprocess.call([editor, str(path)])


def _markdown_path(result: PreprocessResult):
    raise NotImplementedError
